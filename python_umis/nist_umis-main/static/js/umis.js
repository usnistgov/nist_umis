$(document).ready(function() {
    // search and show/hide terms in card
    $("#listsrc").on('keyup',function(){
        let val=$(this).val().toLowerCase().trim();
        let items=$('.item');
        items.show();
        if(val!=='') {
            items.not('[data-content*="' + val + '"]').hide();
        }
    });

    // dynamic update of related select list based on selection from another select
    $(".cascade").on('keyup',function(){

    });
});
