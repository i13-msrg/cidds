
(function ($) {
    "use strict";

    
    /*==================================================================
    [ Validate ]*/
    var name = $('.validate-input input[name="name"]');
    var email = $('.validate-input input[name="email"]');
    var subject = $('.validate-input input[name="subject"]');
    var message = $('.validate-input textarea[name="message"]');


    $('.validate-form').on('submit',function(event){
        var check = true;

        if($(processes).val().trim() == ''){
            showValidate(processes);
            check=false;
        }

        if($(transactions).val().trim() == ''){
            showValidate(transactions);
            check=false;
        }

        if($(alpha).val().trim() == ''){
            showValidate(alpha);
            check=false;
        }

        if($(randomness).val().trim() == ''){
            showValidate(randomness);
            check=false;
        }

        if($(reference).val().trim() == ''){
            showValidate(reference);
            check=false;
        }
        if (!check) {
      event.preventDefault();
    }
        return check;
    });


    $('.validate-form .input1').each(function(){
        $(this).focus(function(){
           hideValidate(this);
       });
    });

    function showValidate(input) {
        var thisAlert = $(input).parent();

        $(thisAlert).addClass('alert-validate');
    }

    function hideValidate(input) {
        var thisAlert = $(input).parent();

        $(thisAlert).removeClass('alert-validate');
    }
    
    

})(jQuery);