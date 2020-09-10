document.addEventListener('DOMContentLoaded', function() {
    let buttons = document.getElementsByClassName('editPost');
    for (var i = 0; i < buttons.length; i++){
        buttons[i].addEventListener('click', function() {edit_post(this.parentElement)}, false);
        console.log("Adding listener");
    }
});

function edit_post(post){

    let elements = post.children;
    console.log(elements);

    let postContent = elements[2].innerHTML;
    console.log(postContent)
    let postElement = elements[2];

    let editArea = document.createElement('textarea');
    editArea.value = postContent;
    postElement.parentNode.replaceChild(editArea, postElement);
}
