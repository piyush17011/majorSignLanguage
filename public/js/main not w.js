// HTML elements
const createUserBtn = document.getElementById("create-user");
const username = document.getElementById("username");
const allusersHtml = document.getElementById("allusers");
const localVideo = document.getElementById("localVideo");
const remoteVideo = document.getElementById("remoteVideo");
const endCallBtn = document.getElementById("end-call-btn");
const muteBtn = document.getElementById("mute-audio-btn");
const videoToggleBtn = document.getElementById("toggle-video-btn");
const shareScreenBtn = document.getElementById("share-screen-btn");  // Share screen button
const stopScreenShareBtn = document.getElementById("stop-screen-share-btn"); 
const predictionText = document.getElementById("predictionText");


// Global variables


let screenStream = null;  // Screen share stream
let localStream = null;  // Local webcam stream
let peerConnection = null;  // WebRTC peer connection
let isScreenSharing = false;  // Flag to track screen sharing status
let caller = [];  // Caller info
let remoteScreenStream = null;  // Remote screen share stream
let isRemoteScreenSharing = false; // Flag to track remote screen sharing status

const socket = io();

// PeerConnection Singleton with Reset Functionality
const PeerConnection = (function() {
    let peerConnection;

    const createPeerConnection = () => {
        const config = {
            iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
        };
        peerConnection = new RTCPeerConnection(config);

        // Add local stream
        if (localStream) {
            localStream.getTracks().forEach(track => {
                peerConnection.addTrack(track, localStream);
            });
        }

        // Listen for remote stream
        peerConnection.ontrack = function(event) {
            remoteVideo.srcObject = event.streams[0];
        };

        // Listen for ICE candidates
        peerConnection.onicecandidate = function(event) {
            if (event.candidate) {
                socket.emit("icecandidate", event.candidate);
            }
        };

        return peerConnection;
    };

    return {
        getInstance: () => {
            if (!peerConnection || peerConnection.connectionState === "closed") {
                peerConnection = createPeerConnection();
            }
            return peerConnection;
        },
        reset: () => {
            peerConnection = null;
        }
    };
})();

// Handle user joining
createUserBtn.addEventListener("click", () => {
    if (username.value !== "") {
        const usernameContainer = document.querySelector(".username-input");
        socket.emit("join-user", username.value);
        usernameContainer.style.display = 'none';
    }
});

// End call event
endCallBtn.addEventListener("click", () => {
    socket.emit("call-ended", caller);
    endCall();
});

// Handle user list
socket.on("joined", (allusers) => {
    allusersHtml.innerHTML = "";
    for (const user in allusers) {
        const li = document.createElement("li");
        li.textContent = ${user} ${user === username.value ? "(You)" : ""};
        
        if (user !== username.value) {
            const button = document.createElement("button");
            button.classList.add("call-btn");
            button.addEventListener("click", () => startCall(user));
            const img = document.createElement("img");
            img.setAttribute("src", "/images/phone.png");
            img.setAttribute("width", 20);
            button.appendChild(img);
            li.appendChild(button);
        }

        allusersHtml.appendChild(li);
    }
});

// Handle offer (receiver)
socket.on("offer", async ({ from, to, offer }) => {
    const pc = PeerConnection.getInstance();
    await pc.setRemoteDescription(offer);
    const answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);
    socket.emit("answer", { from, to, answer: pc.localDescription });

    caller = [from, to];
    endCallBtn.style.display = "block"; // ✅ SHOW END CALL BUTTON
});

// Handle answer (caller)
socket.on("answer", async ({ from, to, answer }) => {
    const pc = PeerConnection.getInstance();
    await pc.setRemoteDescription(answer);

    caller = [from, to];
    endCallBtn.style.display = "block"; // ✅ SHOW END CALL BUTTON
});

// Handle ICE candidates
socket.on("icecandidate", async (candidate) => {
    const pc = PeerConnection.getInstance();
    await pc.addIceCandidate(new RTCIceCandidate(candidate));
});

// Handle end-call event
socket.on("call-ended", () => {
    endCall();
});

// Start call function
const startCall = async (user) => {
    const pc = PeerConnection.getInstance();
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);
    socket.emit("offer", { from: username.value, to: user, offer: pc.localDescription });

    endCallBtn.style.display = "block"; // ✅ SHOW END CALL BUTTON FOR CALLER
};

// End call function
const endCall = () => {
    const pc = PeerConnection.getInstance();
    if (pc) {
        pc.close();
    }

    caller = [];
    endCallBtn.style.display = "none"; // ✅ HIDE END CALL BUTTON
    PeerConnection.reset();
};

// Start local video
async function startMyVideo() {
    try {
        localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        localVideo.srcObject = localStream;
    } catch (error) {
        console.error("Error accessing webcam:", error);
    }
}

// Mute/Unmute audio
muteBtn.addEventListener("click", () => {
    if (localStream) {
        const audioTrack = localStream.getAudioTracks()[0];
        audioTrack.enabled = !audioTrack.enabled;
        muteBtn.textContent = audioTrack.enabled ? "Mute" : "Unmute";
    }
});

// Toggle video on/off
videoToggleBtn.addEventListener("click", () => {
    if (localStream) {
        const videoTrack = localStream.getVideoTracks()[0];
        videoTrack.enabled = !videoTrack.enabled;
        videoToggleBtn.textContent = videoTrack.enabled ? "Video Off" : "Video On";
    }
});

// Initialize the app
startMyVideo();

// Start screen sharing
const startScreenSharing = async () => {
    try {
        // Request the screen sharing stream
        screenStream = await navigator.mediaDevices.getDisplayMedia({ video: true });

        // Set the local video to the screen share stream
        localVideo.srcObject = screenStream;

        // Add the screen sharing tracks to the peer connection
        const pc = PeerConnection.getInstance();

        // First, remove existing webcam video tracks (if any)
        localStream.getTracks().forEach(track => {
            if (track.kind === "video") {
                const sender = pc.getSenders().find(s => s.track.kind === "video");
                if (sender) {
                    sender.replaceTrack(screenStream.getVideoTracks()[0]);
                }
            }
        });

        // Add new screen sharing video track to the peer connection
        screenShareTrack = screenStream.getVideoTracks()[0];  // Store screen share track
        screenStream.getTracks().forEach(track => {
            pc.addTrack(track, screenStream);
        });

        // When the screen sharing stops, restore the webcam stream
        screenStream.getTracks().forEach(track => {
            track.onended = () => {
                stopScreenSharing();  // Stop screen sharing and revert to webcam
            };
        });

        isScreenSharing = true;
    } catch (error) {
        console.error("Error sharing screen:", error);
    }
};

// Stop screen sharing and revert to webcam
const stopScreenSharing = () => {
    if (screenStream) {
        // Stop all screen tracks
        screenStream.getTracks().forEach(track => track.stop());
    }

    // Restore the webcam stream
    localVideo.srcObject = localStream;

    // Replace screen tracks with webcam tracks in the peer connection
    const pc = PeerConnection.getInstance();

    // Remove the screen share track from the peer connection
    const senders = pc.getSenders();
    senders.forEach(sender => {
        if (sender.track === screenShareTrack) {
            sender.replaceTrack(localStream.getVideoTracks()[0]);  // Replace with webcam track
        }
    });

    // Add the webcam stream back to the peer connection
    localStream.getTracks().forEach(track => {
        if (track.kind === "video" && track !== screenShareTrack) {
            pc.addTrack(track, localStream);
        }
    });

    isScreenSharing = false;
};

// Handle screen sharing button
shareScreenBtn.addEventListener("click", () => {
    if (isScreenSharing) {
        stopScreenSharing();  // Stop screen sharing if already active
    } else {
        startScreenSharing();  // Start screen sharing
    }
});

// Handle stop screen share button (optional additional stop button)
stopScreenShareBtn.addEventListener("click", () => {
    stopScreenSharing();  // Stop screen sharing directly
});

// Handle remote screen share functionality
socket.on("remote-screen-share", (stream) => {
    remoteScreenStream = stream;
    remoteVideo.srcObject = remoteScreenStream;  // Show remote screen share
});

// Handle remote user stopping screen share
socket.on("stop-remote-screen-share", () => {
    remoteVideo.srcObject = remoteStream;  // Show webcam video again
});

// Start local video (webcam)
async function startMyVideo() {
    try {
        localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        localVideo.srcObject = localStream;
    } catch (error) {
        console.error("Error accessing webcam:", error);
    }
}