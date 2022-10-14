$(document).ready(function() {
    // search and show/hide terms in card
    $("#listsrc").on('keyup',function(){
        let val=$(this).val().toLowerCase().trim();
        let cons=$('.constant');
        cons.show();
        if(val!=='') {
            cons.not('[data-constant*="' + val + '"]').hide();
        }
    });
});
