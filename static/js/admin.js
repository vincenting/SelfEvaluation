/**
 * Author: Vincent Ting
 * Date: 13-3-16
 * Time: 下午2:54
 */
(function () {

    var box = new BlackBox(),
        xsrftoken = $("input[name=_xsrf]").val();

    if (window.current === "bank") {
        (function () {

            $(document).ready(function () {

                $(".delete").click(function () {
                    var id = $(this).parents("tr")[0].id.split("_")[1];
                    box.confirm("确定要删除么", function (data) {
                        if (!data)return;
                        box.load("delete");
                        var params = {
                            action: 'delete',
                            target: show_list,
                            id: id,
                            _xsrf: xsrftoken
                        };
                        $.ajax({
                            type: "POST",
                            data: params,
                            url: ""
                        }).done(function (data) {
                                if (data == "1") {
                                    location.reload();
                                } else {
                                    box.alert("删除失败，请检查输入后重新提交", {
                                        title: "删除失败"
                                    });
                                }
                            }).always(function () {
                                box.ready("delete");
                            }).fail(function () {
                                box.confirm("网络错误，是否刷新后重试", function (data) {
                                    if (data)location.reload();
                                }, {
                                    title: "网络错误",
                                    value: "刷新页面"
                                })
                            });
                    }, {
                        title: '确定要删除么',
                        value: '删除'
                    });
                    return false;
                });

            })

        })();
    }

}).call(window);