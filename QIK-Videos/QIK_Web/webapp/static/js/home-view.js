$(document).ready(function() {
    // Select dropdown
    $('#id_ranking_function').formSelect();

     // Advance search popup
    $('.modal-trigger').leanModal();

    // Search model dropdown
    $('#id_search_models').formSelect();

    // Loading Screen
    $('.loading-wrapper').hide();
    $("#search").click(function() {
        $(".loading-wrapper").show();
        document.forms['search-form'].submit();
    });

    // Preventing loading the explain tab, without a query image.
    $("#explain").click(function() {
        alert("Please upload an image to search and obtain an explain plan.")
    });

    var indexAlert = $('#indexAlert').text();
    if(indexAlert == "True") {
        alert("Successfully Indexed.");
    }
});


