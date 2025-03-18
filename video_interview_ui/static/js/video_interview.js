document.addEventListener("DOMContentLoaded", function () {
    let mediaRecorder;
    let recordedChunks = [];

    async function getCSRFToken() {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith("csrftoken=")) {
                    cookieValue = cookie.substring("csrftoken=".length, cookie.length);
                    break;
                }
            }
        }
        return cookieValue;
    }

    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
            document.getElementById("videoElement").srcObject = stream;

            mediaRecorder = new MediaRecorder(stream, { mimeType: "video/webm" });

            mediaRecorder.ondataavailable = function (event) {
                if (event.data.size > 0) {
                    recordedChunks.push(event.data);
                }
            };

            mediaRecorder.onstop = async function () {
                const blob = new Blob(recordedChunks, { type: "video/webm" });
                const formData = new FormData();
                formData.append("applicant", document.getElementById("applicant_id").value);
                formData.append("question", document.getElementById("question_id").value);
                formData.append("video_response", blob, "response.webm");

                const csrfToken = await getCSRFToken();

                try {
                    const response = await fetch("http://vhr-backend-bff6bd-546829-65-108-245-140.traefik.me/api/applicant-responses/", {
                        method: "POST",
                        headers: {
                            "X-CSRFToken": csrfToken
                        },
                        body: formData,
                        credentials: "include"
                    });

                    if (response.ok) {
                        alert("Video uploaded successfully!");
                    } else {
                        alert("Failed to upload video.");
                    }
                } catch (error) {
                    console.error("Error uploading video:", error);
                }
            };

            mediaRecorder.start();
        } catch (error) {
            console.error("Error accessing camera:", error);
        }
    }

    function stopRecording() {
        if (mediaRecorder) {
            mediaRecorder.stop();
        }
    }

    document.getElementById("startBtn").addEventListener("click", startRecording);
    document.getElementById("stopBtn").addEventListener("click", stopRecording);
});