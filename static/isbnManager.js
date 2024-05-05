// Event listener for downloading ISBNs
document.getElementById('downloadIsbnBtn').addEventListener('click', function() {
    fetch('http://localhost:8000/textbooks/download-isbns', {
        method: 'GET',
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = "textbook_isbns.txt";
        document.body.appendChild(a);
        a.click();
        a.remove();
    })
    .catch(error => console.error('Error downloading ISBN file:', error));
});

// Event listener for uploading ISBN file
document.getElementById('uploadIsbnFile').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        const formData = new FormData();
        formData.append('file', file);

        fetch('http://localhost:8000/textbooks/upload-isbns', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log('Upload successful:', data);
        })
        .catch(error => console.error('Error uploading ISBN file:', error));
    }
});
