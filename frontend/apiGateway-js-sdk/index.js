var apigClient = apigClientFactory.newClient();

function searchByVoice() {
    var SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.start();
    recognition.onresult = (event) => {
        const speechToText = event.results[0][0].transcript;
        console.log(speechToText);
        document.getElementById("searchQuery").value = speechToText;
        //textSearch(); 
    }
}

function textSearch() {
    var searchText = document.getElementById('searchQuery');
    if (!searchText.value) {
        alert('Please enter a valid text or voice input.');
    } else {
        searchText = searchText.value.trim().toLowerCase();
        console.log('Searching Photos....');
        searchByText(searchText);
    }
    
}

function searchByText(){
    var searchTerm = document.getElementById("searchQuery").value;
    document.getElementById('searchResults').innerHTML = "<h4 style=\"text-align:center\">";

    var params = {q: searchTerm};

    apigClient.searchGet(params, {}, {})
        .then(function(res){
            console.log("success");
            console.log("Result: ",res);
            
            image_paths = result["data"]["body"]["imagePaths"];
            console.log("image_paths:", image_paths)

            var photoDiv = document.getElementById("searchResult")
            photosDiv.innerHTML = "";

            var n;
            for (n = 0; n < image_paths.length; n++) {
                images_list = image_paths[n].split('/');
                imageName = images_list[images_list.length - 1];

                photosDiv.innerHTML += '<figure><img src="' + image_paths[n] + '" style="width:25%"><figcaption>' + imageName + '</figcaption></figure>';
            }

    }).catch(function(result){
        console.log(result);
        console.log("No result");
    });
}


function uploadImage() {

    var filePath = (document.getElementById('photoUpload').value).split('\\');
    var fileName = filePath[filePath.length - 1];

    if(document.getElementById('labels') != ""){
        var customLabels = document.getElementById('labels').value;
    }
    console.log(filePath);
    console.log(fileName);
    console.log(customLabels);
    var reader = new FileReader();
    var file = document.getElementById('photoUpload').files[0];
    console.log('File:', file);
    document.getElementById('photoUpload').value = "";

    var params = {
        bucket: 'photo-bucket-2397',
        key: fileName,
        'Content-Type': file.type,
        'x-amz-meta-customLabels': customLabels
        
    };

    // var additionalParams = {
    //     headers:{
    //         'x-amz-meta-customLabels': customLabels,
    //         "Content-Type": "image/jpg"
    //     }
    // }
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