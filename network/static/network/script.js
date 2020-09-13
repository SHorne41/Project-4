document.addEventListener('DOMContentLoaded', function() {
    //Retrieve all "Edit Post" buttons and add event listeners to them
    let editButtons = document.getElementsByClassName('editPost');
    for (var i = 0; i < editButtons.length; i++){
        editButtons[i].addEventListener('click', function() {edit_post(this.parentElement)});    //this.parentElement refers to the <div> containing the entire post
    }

    //Retrieve all "Like Post" buttons and add event listeners to them
    let likeButtons = document.getElementsByClassName('likePost');
    for (var i = 0; i < likeButtons.length; i++){
        likeButtons[i].addEventListener('click', function() {like_post(this.parentElement)});    //this.parentElement refers to the <div> containing the entire post
    }
});

function like_post(post){
    //Retrieve all children of the post <div>
    let elements = post.children;
    console.log(elements)

    //Retrieve the <p> element displaying the number of likes
    let likeCounter = elements[3].innerHTML;
    let numLikes = likeCounter.substring(7);

    //Convert string representation of numLikes into integer, then increment
    let intLikes = parseInt(numLikes, 10);
    intLikes += 1;

    //Update post with new numLikes
    updatedLikeCounter = likeCounter.substring(0, 7) + intLikes;
    elements[3].innerHTML = updatedLikeCounter;

    //Make request to server to updated number of likes
    let postContent = elements[2].innerHTML;        //Used to retrieve appropriate post from database
    fetch('/updateLikes', {
        method: 'PUT',
        body: JSON.stringify({
            owner: elements[0].innerHTML.substring(4, (elements[0].innerHTML.length - 5)),
            postContent: postContent,
            newLikeCount: intLikes,
        })
    })
    .then (response => response.json())
    .then(result => {
        console.log("Like count updated successfully");
    });

}

function edit_post(post){
    //Retrieve all children of the post <div>
    let elements = post.children;

    //Retrieve the <p> element containing the post content
    let postContent = elements[2].innerHTML;
    let postElement = elements[2];

    //Create a textarea autopopulated with the post content where the user can edit the post
    let editArea = document.createElement('textarea');
    editArea.style.width = "75%";
    editArea.style.height = "150px"
    editArea.value = postContent;

    //Replace the postElement with the textarea and hide the "edit post" button
    postElement.parentNode.replaceChild(editArea, postElement);
    elements[4].style.visibility = "hidden";

    //Create a "Save Changes" button and add it to the DOM
    let saveChanges = document.createElement('button');
    saveChanges.innerHTML = "Save";

    //Update the post in the database once the user clicks the "Save Changes" button
    saveChanges.addEventListener('click', function () {
        fetch('/editPost', {
            method: 'PUT',
            body: JSON.stringify({
                owner: elements[0].innerHTML.substring(4, (elements[0].innerHTML.length - 5)),
                postContent: postContent,
                updatedContent: editArea.value
            })
        })
        .then(response => response.json())
        .then(result => {
            //Delete save button and 'unhide' edit button
            saveChanges.remove();
            elements[4].style.visibility = "visible";

            //Replace the textarea with a <p> element; updated post content
            let updatedPost = document.createElement('p');
            updatedPost.innerHTML = editArea.value;
            editArea.parentNode.replaceChild(updatedPost, editArea);
        });
    });
    post.appendChild(saveChanges);
}
