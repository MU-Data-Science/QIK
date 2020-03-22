$(document).ready(function() {
  var FEEDBACK_URL = "128.110.154.250"

  $( "#tabs" ).tabs();

  $("#feedback img").click(function() {
    var id = $(event.target).attr("id")
    url = "http://" + FEEDBACK_URL + ":8080/IndexEngine/feedback?data=" + id
    $.get(url, function(data, status){
      alert("Thank you for the feedback.");
    });
  });

  $("#resultImage").click(function(event) {
    var imageURL = $(event.target).attr("src");
    url = "http://" + FEEDBACK_URL + ":8080/IndexEngine/imgclick?data="
    $.get(url, function(data, status){
      console.log("Successfully logged")
    });
  });

  $("span.buttonText").text("Choose a directory")
  $("#image_search").find("span.buttonText").text("Choose an Image File")
  $("#text_search").find("span.buttonText").text("Choose a Search Text")

});

$( function() {
  $.widget( "custom.iconselectmenu", $.ui.selectmenu, {
    _renderItem: function( ul, item ) {
      var li = $( "<li>" ),
          wrapper = $( "<div>", { text: item.label } );

      if ( item.disabled ) {
        li.addClass( "ui-state-disabled" );
      }

      $( "<span>", {
        style: item.element.attr( "data-style" ),
        "class": "ui-icon " + item.element.attr( "data-class" )
      })
          .appendTo( wrapper );

      return li.append( wrapper ).appendTo( ul );
    }
  });

  $( "#images" )
      .iconselectmenu()
      .iconselectmenu( "menuWidget")
      .addClass( "ui-menu-icons avatar" );
} );

