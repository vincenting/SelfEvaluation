/**
 * Author: Vincent Ting
 * Date: 13-3-18
 * Time: 下午1:52
 */
(function () {

    var box = new BlackBox(),
        subjects_queue = [],
        result_choices = {},
        start_time,
        setEvaluation = function (list, callback) {
            if (list.length == 0) {
                callback = callback || $.noop;
                callback.call(this, result_choices);
                return;
            }
            var current_data = list.pop();
            current_data.choices = _.shuffle(current_data.choices);
            current_data.is_next = list.length > 0;
            var template = $("#evaluation_template").html();
            box.popup(_.template(template, current_data), function (evaluation) {
                var current_choices = [], current_ids = [],
                    $current_choices = evaluation.find("#current_choices");
                evaluation.find("#evaluation_bar").delegate("li", "click", function () {
                    var attr_id = this.id.split("_"),
                        id = attr_id[1], choice_name = attr_id[0];
                    if (this.className == "selected") {
                        this.className = "";
                        current_choices = _.without(current_choices, choice_name);
                        current_ids = _.without(current_ids, id);
                    } else {
                        this.className = "selected";
                        current_choices.push(choice_name);
                        current_ids.push(id);
                    }
                    $current_choices.text(current_choices.length ? current_choices.join(", ") : '暂无');
                });
                evaluation.find("#finishEvaluation").click(function () {
                    result_choices[current_data.id]  = current_ids;
                    box.boxClose();
                    setEvaluation(list, callback);
                });
            });
        };

    $(document).ready(function () {
        box.load("page");
        box.load("subjects");
        var sendDataToServer = function (study_data) {
            box.load("update");
            data['_xsrf'] = $("input[name=_xsrf]").val();
            $.ajax({
                type: "POST",
                url: "/",
                data: data
            }).done(function (data) {
                    box.alert("你的作答情况为" + data, function () {
                        location.reload();
                    }, {title: "恭喜你作答结束",
                        value: "结束答题"})
                }).fail(function () {
                    box.confirm("网络错误，是否刷新后重试", function (again) {
                        if (again) {
                            box.boxClose();
                            sendDataToServer(study_data);
                        }
                    }, {
                        title: "网络错误",
                        value: "重新提交"
                    })
                }).always(function () {
                    box.ready("update");
                });
        };
        $("#startEvaluation").click(function () {
            start_time = (new Date()).valueOf();
            setEvaluation(subjects_queue, function (data) {
                var study_data = {
                    spend_time: (new Date()).valueOf() - start_time,
                    choice_data: $.toJSON(data)
                };
                sendDataToServer(study_data);
            });

        });

    });

    $.ajax({
        type: "GET",
        url: "/?get=subjects"
    }).done(function (data) {
            if (!data)return;
            if(data == "Finish"){
                $("#startEvaluation").fadeOut();
                box.alert("您已经完成当前章节的学习",{
                    title:'预习完成'
                })
            }else{
                subjects_queue = $.parseJSON(data);
            }
        }).always(function () {
            box.ready("subjects");
        }).fail(function () {
            box.confirm("网络错误，是否刷新后重试", function (data) {
                if (data)location.reload();
            }, {
                title: "网络错误",
                value: "刷新页面"
            })
        });

    window.onload = function () {
        box.ready("page");
    };

}).call(window);