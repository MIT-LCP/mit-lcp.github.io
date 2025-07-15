  function readURL(input){
  $("#crop_pic").css("display", "block");

  if (input.files && input.files[0]) {
    var reader = new FileReader();
    reader.onload = function (e) {
      $("#image").attr("src", e.target.result);
    }
    reader.readAsDataURL(input.files[0]);
    setTimeout(initCropper, 1000);
  }
}
  function initCropper(){

      var image = document.getElementById('image');
      var cropper = new Cropper(image, {
        viewMode: 1,
        aspectRatio: 1 / 1,
        minCropBoxWidth: 200,
        minCropBoxHeight: 200,
        maxCropBoxWidth:400,
        maxCropBoxHeight:400,
        crop: function(event) {
          $("#id_x").val(event.detail.x);
          $("#id_y").val(event.detail.y);
          $("#id_height").val(event.detail.height);
          $("#id_width").val(event.detail.width);
        }
      });  
};
