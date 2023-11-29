var apigClient = apigClientFactory.newClient();
var SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;


function searchByVoice() { 
    const recognition = new SpeechRecognition();
    recognition.start();
    recognition.onresult = (event) => {
      const speechToText = event.results[0][0].transcript;
      console.log(speechToText);
      document.getElementById("searchQuery").value = speechToText;
      textSearch();
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

}