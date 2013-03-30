/**
 * Author: Vincent Ting
 * Date: 13-3-18
 * Time: 下午1:52
 */
(function () {

    var box = new BlackBox(),
        subjects_queue = [],
        result_choices = [],
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
                    result_choices.push({
                        id: current_data.id,
                        choices: current_ids
                    });
                    box.boxClose();
                    setEvaluation(list, callback);
                });
            });
        };

    $(document).ready(function () {
        box.load("page");
        box.load("subjects");
        $("#startEvaluation").click(function () {
            setEvaluation(subjects_queue,function(data){
                console.log(data);
            });
        });

    });

    $.ajax({
        type: "GET",
        url: "/?get=subjects"
    }).done(function (data) {
            if (!data)return;
            subjects_queue = $.parseJSON(data);
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