document.addEventListener('DOMContentLoaded', function() {
    let buttons = document.getElementsByClassName('editPost');
    for (var i = 0; i < buttons.length; i++){
        buttons[i].addEventListener('click', function() {edit_post(this.parentElement)});    //this.parentElement refers to the <div> containing the entire post
    }
});

function edit_post(post){

    //Retrieve all children of the post <div>
    let elements = post.children;
    console.log(elements[0].innerHTML.length);
    console.log(elements[0].innerHTML.substring(4, (elements[0].innerHTML.length - 5)));

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
