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
            <button type="submit" style="margin-top:10px; padding:10px 20px;">Submit & Download</button>
        </form>
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
            alert("Thank you! Redirecting to the download page.");
            window.location.href = "https://github.com/msdev87/Cilialyzer/releases/tag/Cilialyzer-v1.5.0-f1dc712";
        } else {
            alert("Failed to submit. Please check your input and try again.");
        }
    }).catch(error => {
        console.error("Error:", error);
        alert("An error occurred. Please try again.");
    });
}
</script>






















 

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
            <button type="submit" style="margin-top:10px; padding:10px 20px;">Submit & Download</button>
        </form>
    </div>
</div>

<script>
// Show the modal when the download link is clicked
function showDownloadForm() {
    document.getElementById('downloadModal').style.display = 'flex';
}

// Handle form submission
function submitForm(event) {
    event.preventDefault(); // Prevent the form from refreshing the page
    
    const email = document.getElementById('email').value;
    
    // Send the email to Formspree or another email service
    fetch("https://formspree.io/f/mgveyeql", {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email, timestamp: new Date() })
    }).then(response => {
        if (response.ok) {
            // Redirect to download after form submission
            window.location.href = "https://github.com/msdev87/Cilialyzer/releases/tag/Cilialyzer-v1.5.0-f1dc712";
        } else {
            alert("Something went wrong. Please try again.");
        }
    }).catch(error => {
        console.error("Error:", error);
        alert("An error occurred. Please try again.");
    });
}
</script>
















<!--
<b> Dear visitor, if you use Cilialyzer, please contact us via e-mail: martin.schneiter@gmx.ch. </b>

We would be happy to keep our users up-to-date and notify them by e-mail as soon as a new version of Cilialyzer has been made available. 
And we would also like to learn more about who is using our software and for what purpose. 
We would therefore very much appreciate to receive your short notification by e-mail to the above address.

<br />
<div align="center"> 
   <font size="+2">
   <b> Download the most recent binary release for Windows below: </b>
   </font>
</div>
<br />
<div align="center">
   <b>
   <font size="+2"> <a href="https://github.com/msdev87/Cilialyzer/releases/tag/Cilialyzer-v1.5.0-f1dc712" download="">Cilialyzer-v1.5.0-f1dc712</a> (creation date: July 18, 2024) </font>
   </b>
</div> 
<br />
-->




<!--
<br />
<div align="center"> 
   <font size="+2">
   <b> Download the most recent binary release for Windows below: </b>
   </font>
</div>
<br />
<div align="center">
   <b>
   <font size="+2"> <a href="https://github.com/msdev87/Cilialyzer/releases/tag/Cilialyzer-v1.3.0-46218df" download="">Cilialyzer-v1.3.0-46218df</a> (creation date: November 5, 2023) </font>
   </b>
</div> 
<br />
<br />
-->




<!--
<b>List of most important changes made to version 1.2.0:</b>  <br />

<b> Acitivity map:</b>  <br />
The calculation of the activity map has been heavily revised. 
The current calculation correlates now well with our visual assessment of the proportion of active cilia. 
We will provide here a link to a report of the newly implemented algorithm. 

<b> Pixel Binning: </b>  <br />
A 'Pixel Binning' button has been added to the ROI-selection tab. If pressed, a 2x2 pixel binning (cubic interpolation) is performed. 
Please note that it may make sense to perform a pixel binning, as many calculations are time-consuming and/or memory-intensive. 

<b> Image stabilization: </b>  <br />
In most cases it should no longer be necessary to manually crop the video after performing an image stabilization, as the video gets now cropped automatically after having been stabilized. 

<b> ROI-selection: </b>  <br />
A region of interest can now be selected repeatedly. 

<b> Image rotation: </b>  <br />
Bug considering the image rotation has now been solved. (After having been rotated, the video does now actually remain rotated.) 



____________________________________________________________________________________________________________

Cilialyzer version 1.2.0 was described in our first publication on Cilialyzer (<a href="./publications.md">Download publication</a>).

<br />   
   <a href="https://github.com/msdev87/Cilialyzer/releases/tag/Cilialyzer-v1.2.1-b3098cb" download="">Cilialyzer-v1.2.1-b3098cb</a> (creation date: July 18, 2023)
<br />



<!--
<br />
<div align="center">      
   <a href="Cilialyzer-v1.2.0-67303f.zip" download="">Cilialyzer-v1.2.0-67303f.zip</a> (creation date: January 22, 2022)
</div> 
<div align="center">      
   <a href="Cilialyzer-v1.1.1-048a3b.zip" download="">Cilialyzer-v1.1.1-048a3b.zip</a> (creation date: October 4, 2022)
</div> 
<div align="center">      
   <a href="Cilialyzer-v1.0.0-91f24d4.zip" download="">Cilialyzer-v1.0.0-91f24d4.zip</a> (creation date: December 13, 2021)
</div> 
-->
   

<br />

