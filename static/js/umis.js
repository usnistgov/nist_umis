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
});
