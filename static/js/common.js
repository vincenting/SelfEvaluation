/**
 * Author: Vincent Ting
 * Date: 13-3-13
 * Time: 下午7:58
 */
(function () {

    window.common = {};

    var Verification = {
        required: function (val) {
            return !!val;
        },
        email: function (val) {
            return /^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$/.test(val);
        },
        ccnu_id: function (val) {
            return /^[0-9]+$/.test(val);
        }
    };
    common.validate = function ($form) {
        var $inputs = $form.find("input"),
            result = true;
        $inputs.each(function () {
            $(this).val($.trim($(this).val()));
            var validates = $(this).attr("validate") && $(this).attr("validate").split(" ");
            if (!validates)return;
            var val = $(this).val(), $this = $(this);
            jQuery.each(validates, function (index, role) {
                if (!Verification[role])return;
                if (!Verification[role](val)) {
                    $this.addClass("error");
                    result = false;
                }
            });
        });
        return result;
    };
    $(document).on("focus", "input", function () {
        $(this).removeClass("error");
    });


}).call(window);