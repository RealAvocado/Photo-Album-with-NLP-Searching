var apigClient = apigClientFactory.newClient();

//voice to text
function searchByVoice() {
    var SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.start();
    recognition.onresult = (event) => {
        const speechToText = event.results[0][0].transcript;
        console.log(speechToText);
        document.getElementById("searchQuery").value = speechToText;
    }
}

//text search check
function textSearch() {
    var searchText = document.getElementById('searchQuery');
    if (!searchText.value) {
        alert('Please enter a valid text or voice input.');
    } else {
        searchByText();
    }
    
}

//search by text and receive url
function searchByText(){
    console.log("triggered searchByText");
    var query = document.getElementById("searchQuery").value;

    var params = {q: query};
    console.log(params);

    document.getElementById('searchForm').reset();


    apigClient.searchGet(params, {}, {})
        .then(function(res){
            console.log("success");
            console.log("Result: ",res);
            
            image_paths = res.data
            console.log("image_paths:", image_paths[0])

            var photoDiv = document.getElementById("searchResults")
            photoDiv.innerHTML = "";

            var n;
            for (n = 0; n < image_paths.length; n++) {
                images_list = image_paths[n].split('/');
                photoDiv.innerHTML += '<figure><img src="' + image_paths[n] + '"style="width:50%"></figure>';
            }

    }).catch(function(result){
        console.log(result);
        console.log("No result");
    });
}

// upload image to S3
function uploadImage() {
    var filePath = (document.getElementById('photoUpload').value).split('\\');
    var fileName = filePath[filePath.length - 1];

    var labelsInput = document.getElementById('labels');
    if(labelsInput && labelsInput.value != ""){
        var customLabels = labelsInput.value;
        labelsInput.value = "";
    }

    console.log(filePath);
    console.log(fileName);
    console.log(customLabels);
    var reader = new FileReader();
    var file = document.getElementById('photoUpload').files[0];
    console.log('File:', file);
    document.getElementById('uploadForm').reset();



    var params = {
        bucket: 'photo-bucket-2397',
        key: fileName,
        'Content-Type': file.type,
        'x-amz-meta-customLabels': customLabels
        
    };

    reader.readAsBinaryString(file);
    reader.onload = function(event){
        body = btoa(event.target.result);
        console.log('Reader body:', body)

        return apigClient.uploadBucketKeyPut(params, body)
        .then(function(res){
            console.log(res);
        })
        .catch(function(err){
            console.log(err);
        })
    }

}