$(document).ready(function() {
    // search and show/hide terms in card
    $("#listsrc").on('keyup',function(){
        let val=$(this).val().toLowerCase().trim();
        let items=$('.item');
        let units =$('.units');
        let qks =$('.qkind');
        if (qks) { qks.show(); }
        if (units) { units.show(); }
        items.show();
        if(val!=='') {
            items.not('[data-content*="' + val + '"]').hide();
            qks.each(function () {
                let qk = $(this);
                if (qk.find('a:visible').length === 0) {
                    qk.hide();
                }
            });
        }
    });

    // dynamic update of related select list based on selection from another select
    $(".cascade").on('keyup',function(){

    });
});
