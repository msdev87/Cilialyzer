<div align="center"> 
   <a href="./index.html" style="font-size:25px;font-weight:400;"       >Home</a>  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
   <a href="./download.html" style="font-size:25px;font-weight:600;"     >Download</a>  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
   <a href="./tutorials.html" style="font-size:25px;font-weight:400;"    >Tutorials</a> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
   <a href="./pinboard.html" style="font-size:25px;font-weight:400;"     >Pinboard</a>  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
   <a href="./publications.html" style="font-size:25px;font-weight:400;" >Publications</a> 
</div> 


<br />
<br />

<!-- The download link that triggers the modal -->
<a href="#" onclick="showDownloadForm()">Download the latest Cilialyzer version</a>

<!-- Modal Form HTML -->
<div id="downloadModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); align-items:center; justify-content:center;">
    <div style="background:#fff; padding:20px; border-radius:5px; max-width:500px; width:90%;">
        <h3>Dear colleague, we are currently gathering information about the users of our software and their specific use cases.
            Please provide us with the following details: </h3>
        <form id="downloadForm" onsubmit="submitForm(event)">
            <label for="email">Your email:</label>
            <input type="email" id="email" name="email" required style="width:100%; padding:8px; margin-top:10px;">
            <label for="name">Your name:</label>
            <input type="text" id="name" name="name" required style="width:100%; padding:8px; margin-top:10px;">
            <label for="purpose">Use case:</label>
            <textarea id="purpose" name="purpose" required style="width:100%; padding:8px; margin-top:10px;"></textarea>
            <button type="submit" style="margin-top:10px; padding:10px 20px;">Submit & Proceed</button>
        </form>
    </div>
</div>

<!-- Redirect Modal HTML -->
<div id="redirectModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); align-items:center; justify-content:center;">
    <div style="background:#fff; padding:20px; border-radius:5px; max-width:500px; width:90%;">
        <h3>Thank you for your submission! You can now proceed to the download page.</h3>
        <button onclick="redirectToDownload()" style="padding:10px 20px;">Go to Download</button>
    </div>
</div>

<script>
// Show the modal when the download link is clicked
function showDownloadForm() {
    const modal = document.getElementById('downloadModal');
    modal.style.display = 'flex';

    // Close modal on Escape key press
    document.addEventListener('keydown', function handleEscape(event) {
        if (event.key === 'Escape') {
            closeDownloadModal();
            document.removeEventListener('keydown', handleEscape);
        }
    });
}

// Close the modal
function closeDownloadModal() {
    document.getElementById('downloadModal').style.display = 'none';
}

// Handle form submission
function submitForm(event) {
    event.preventDefault(); // Prevent the form from refreshing the page

    // Gather form data
    const formData = new FormData(document.getElementById('downloadForm'));

    // Send the form data to Formspree
    fetch("https://formspree.io/f/mgveyeql", {
        method: "POST",
        body: formData
    }).then(response => {
        if (response.ok) {
            // Close the initial modal before showing the redirect modal
            closeDownloadModal();

            // Optionally show the redirect modal
            document.getElementById('redirectModal').style.display = 'flex';

            // Redirect immediately to the download page after form submission
            setTimeout(redirectToDownload, 2000); // Redirect after a short delay (2 seconds)

        } else {
            // On failure, redirect to the download page directly
            alert("You will be redirected to the download page.");
            redirectToDownload();
        }
    }).catch(error => {
        console.error("Error:", error);
        alert("You will be redirected to the download page.");
        redirectToDownload();
    });
}

// Redirect to the download page after the user clicks the "Go to Download" button or after a delay
function redirectToDownload() {
    window.location.href = "https://github.com/msdev87/Cilialyzer/releases/tag/Cilialyzer-v1.5.0-f1dc712";
}
</script>




















