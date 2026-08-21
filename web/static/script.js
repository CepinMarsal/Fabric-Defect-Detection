/**
 * script.js — Computer Vision Project
 * Handles: Camera selection & streaming, animations, navigation
 */

(function () {
    "use strict";

    // ============================
    // DOM Elements
    // ============================
    const cameraSelect = document.getElementById("cameraSelect");
    const btnStart = document.getElementById("btnStart");
    const btnStop = document.getElementById("btnStop");
    const cameraFeed = document.getElementById("cameraFeed");
    const cameraPlaceholder = document.getElementById("cameraPlaceholder");
    const cameraStatus = document.getElementById("cameraStatus");
    const recordingDot = document.getElementById("recordingDot");
    const resultFeed = document.getElementById("resultFeed");
    const captureCanvas = document.getElementById("captureCanvas");

    // ============================
    // State
    // ============================
    let currentStream = null;
    let isProcessing = false;
    let processingInterval = null;

    // ============================
    // CAMERA — Enumerate Devices
    // ============================

    /**
     * Mengambil daftar kamera yang tersedia pada device.
     * Setelah permission diberikan, refresh daftar untuk mendapatkan label kamera.
     */
    async function enumerateCameras() {
        try {
            // Cek apakah browser mendukung mediaDevices
            if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) {
                setStatus("Browser tidak mendukung akses kamera.", "error");
                return;
            }

            const devices = await navigator.mediaDevices.enumerateDevices();
            const videoDevices = devices.filter(function (d) {
                return d.kind === "videoinput";
            });

            // Simpan pilihan sebelumnya
            var previousValue = cameraSelect.value;

            // Bersihkan dropdown
            cameraSelect.innerHTML = "";

            // Option default
            var defaultOption = document.createElement("option");
            defaultOption.value = "";
            defaultOption.textContent = "-- Pilih Kamera --";
            cameraSelect.appendChild(defaultOption);

            if (videoDevices.length === 0) {
                setStatus("Tidak ada kamera terdeteksi pada device.", "error");
                return;
            }

            // Tambahkan setiap kamera ke dropdown
            videoDevices.forEach(function (device, index) {
                var option = document.createElement("option");
                option.value = device.deviceId;
                option.textContent = device.label || "Kamera " + (index + 1);
                cameraSelect.appendChild(option);
            });

            // Kembalikan pilihan sebelumnya jika masih ada
            if (previousValue) {
                cameraSelect.value = previousValue;
            }
        } catch (err) {
            console.error("Error enumerating devices:", err);
            setStatus("Gagal mendeteksi kamera: " + err.message, "error");
        }
    }

    /**
     * Minta permission kamera terlebih dahulu, kemudian refresh daftar kamera.
     * Ini diperlukan karena beberapa browser tidak memberikan label kamera
     * sebelum permission diberikan.
     */
    async function requestPermissionAndEnumerate() {
        try {
            // Request permission dengan getUserMedia sederhana
            var tempStream = await navigator.mediaDevices.getUserMedia({ video: true });
            // Langsung stop, kita hanya butuh permission
            tempStream.getTracks().forEach(function (track) {
                track.stop();
            });
            // Sekarang enumerate ulang — label kamera akan tersedia
            await enumerateCameras();
        } catch (err) {
            if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
                setStatus("Permission kamera ditolak. Izinkan akses kamera pada browser.", "error");
            } else if (err.name === "NotFoundError") {
                setStatus("Tidak ada kamera ditemukan pada device.", "error");
            } else {
                setStatus("Error: " + err.message, "error");
            }
            console.error("Permission error:", err);
        }
    }

    // ============================
    // CAMERA — Start / Stop
    // ============================

    /**
     * Membuka kamera berdasarkan deviceId yang dipilih user.
     */
    async function startCamera() {
        var selectedDeviceId = cameraSelect.value;

        if (!selectedDeviceId) {
            setStatus("Pilih kamera terlebih dahulu.", "error");
            return;
        }

        // Jika ada stream aktif, stop terlebih dahulu
        if (currentStream) {
            stopCamera();
        }

        try {
            setStatus("Membuka kamera...", "");

            var constraints = {
                video: {
                    deviceId: { exact: selectedDeviceId },
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                }
            };

            var stream = await navigator.mediaDevices.getUserMedia(constraints);
            currentStream = stream;

            cameraFeed.srcObject = stream;
            cameraFeed.style.display = "block";
            
            // Tunggu sampai video bermain untuk mendapatkan ukuran frame
            cameraFeed.onplaying = () => {
                captureCanvas.width = cameraFeed.videoWidth;
                captureCanvas.height = cameraFeed.videoHeight;
                
                // Mulai proses pengiriman frame hanya jika belum berjalan
                if (!isProcessing) {
                    isProcessing = true;
                    processFrame();
                }
            };
            
            // Panggil play secara eksplisit
            cameraFeed.play().catch(e => console.error("Play error:", e));

            cameraPlaceholder.style.display = "none";
            // resultFeed disembunyikan dulu sampai frame pertama berhasil diproses
            resultFeed.style.display = "none";
            recordingDot.style.display = "block";

            btnStart.disabled = true;
            btnStop.disabled = false;

            setStatus("Kamera aktif (Memproses Real-time...)", "active");

        } catch (err) {
            if (err.name === "NotAllowedError") {
                setStatus("Permission kamera ditolak. Izinkan akses kamera.", "error");
            } else if (err.name === "NotReadableError") {
                setStatus("Kamera sedang digunakan oleh aplikasi lain.", "error");
            } else if (err.name === "OverconstrainedError") {
                setStatus("Kamera yang dipilih tidak tersedia.", "error");
            } else {
                setStatus("Gagal membuka kamera: " + err.message, "error");
            }
            console.error("Camera start error:", err);
        }
    }

    /**
     * Menghentikan kamera dan membersihkan stream.
     */
    function stopCamera() {
        isProcessing = false; // Hentikan loop pemrosesan

        if (currentStream) {
            currentStream.getTracks().forEach(function (track) {
                track.stop();
            });
            currentStream = null;
        }

        cameraFeed.srcObject = null;
        cameraFeed.style.display = "none";
        resultFeed.style.display = "none";
        resultFeed.src = ""; // Bersihkan gambar terakhir
        cameraPlaceholder.style.display = "flex";
        recordingDot.style.display = "none";

        btnStart.disabled = false;
        btnStop.disabled = true;

        setStatus("Kamera dihentikan.", "");
    }

    /**
     * Set status text dan class pada elemen status kamera.
     * @param {string} message - Pesan status
     * @param {string} type - "active", "error", atau "" (default)
     */
    function setStatus(message, type) {
        cameraStatus.textContent = message;
        cameraStatus.className = "camera-status";
        if (type) {
            cameraStatus.classList.add(type);
        }
    }

    /**
     * Memproses frame secara berulang dengan mengirimkannya ke backend Flask.
     */
    async function processFrame() {
        if (!isProcessing) return;

        try {
            if (captureCanvas.width === 0 || captureCanvas.height === 0) {
                // Tunggu sebentar sampai ukuran tersedia
                if (isProcessing) setTimeout(() => requestAnimationFrame(processFrame), 100);
                return;
            }

            // Gambar frame saat ini ke canvas
            const ctx = captureCanvas.getContext('2d');
            ctx.drawImage(cameraFeed, 0, 0, captureCanvas.width, captureCanvas.height);
            
            // Ambil data base64
            const imageData = captureCanvas.toDataURL('image/jpeg', 0.8);

            // Kirim ke backend
            const response = await fetch('/api/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ image: imageData })
            });

            const data = await response.json();
            
            if (data.success && isProcessing) {
                // Tampilkan hasil pemrosesan dan sembunyikan video asli di belakangnya jika perlu
                resultFeed.src = data.image;
                if (resultFeed.style.display === "none") {
                    resultFeed.style.display = "block";
                }
            } else if (data.error) {
                console.error("Error dari backend:", data.error);
            }
        } catch (error) {
            console.error("Gagal memproses frame:", error);
        }

        // Jalankan rekursif untuk frame berikutnya jika masih aktif
        if (isProcessing) {
            // Gunakan requestAnimationFrame atau timeout (misal tiap 100ms untuk meringankan beban)
            setTimeout(() => {
                requestAnimationFrame(processFrame);
            }, 100); 
        }
    }

    // ============================
    // CAMERA — Event Listeners
    // ============================
    btnStart.addEventListener("click", startCamera);
    btnStop.addEventListener("click", stopCamera);

    // Jika user mengganti kamera saat stream aktif, restart kamera
    cameraSelect.addEventListener("change", function () {
        if (currentStream && cameraSelect.value) {
            startCamera();
        }
    });

    // ============================
    // ANIMASI — IntersectionObserver
    // ============================
    var fadeElements = document.querySelectorAll(".fade-in");

    if ("IntersectionObserver" in window) {
        var observer = new IntersectionObserver(
            function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("visible");
                        observer.unobserve(entry.target);
                    }
                });
            },
            {
                threshold: 0.15,
                rootMargin: "0px 0px -50px 0px"
            }
        );

        fadeElements.forEach(function (el) {
            observer.observe(el);
        });
    } else {
        // Fallback: langsung tampilkan semua
        fadeElements.forEach(function (el) {
            el.classList.add("visible");
        });
    }

    // ============================
    // INIT
    // ============================

    /**
     * Inisialisasi: enumerate kamera, request permission jika diperlukan.
     */
    async function init() {
        // Pertama, coba enumerate tanpa permission
        await enumerateCameras();

        // Jika label kosong (permission belum diberikan), minta permission
        var options = cameraSelect.querySelectorAll("option");
        var needsPermission = false;
        options.forEach(function (opt) {
            if (opt.value && opt.textContent.startsWith("Kamera ")) {
                needsPermission = true;
            }
        });

        if (needsPermission && options.length > 1) {
            // Label belum tersedia, permission belum diberikan
            // Kita tetap tampilkan daftar, user bisa tekan "Buka Kamera"
            // Permission akan diminta saat kamera dibuka
            setStatus("Pilih kamera dan tekan Buka Kamera.", "");
        }
    }

    init();
})();
