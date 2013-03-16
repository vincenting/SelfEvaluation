/**
 * Author: Vincent Ting
 * Date: 13-3-13
 * Time: 上午10:29
 */
(function () {

    var box = new BlackBox(),
        $W = $(window);

    $(document).ready(function () {

        $("#login_form").find('input, textarea').placeholder();

        var xsrftoken = $("input[name=_xsrf]").val();

        box.load("page");
        var $index_wrap = $("#index_wrap"),
            index_height = 400, _height,
            resize_height = function () {
                if (index_height < $W.height()) {
                    _height = $W.height();
                } else {
                    _height = index_height;
                }
                $index_wrap.height(_height);
                $("#index_content").css({
                    top: (_height / 2 - 150) + 'px'
                })
            };
        $W.resize(resize_height);
        resize_height.call(this);

        $("#login_do").click(function () {
            if (!common.validate($("#login_form"))) {
                box.alert("请检查输入信息后再次登录", {
                    title: "输入有误"
                });
                return false;
            }
            var params = {
                _xsrf: xsrftoken,
                action: 'login',
                email: $("#login_email").val(),
                password: $("#login_psw").val()
            };
            box.load("login");
            $.ajax({
                type: "POST",
                data: params,
                url: "/account.do"
            }).done(function (data) {
                    if (data == "1") {
                        location.reload();
                    } else {
                        box.alert("登录失败，请检查帐号后重新输入", {
                            title: "登录失败"
                        });
                        $("#login_form").find("input").addClass("error");
                    }
                }).always(function () {
                    box.ready("login");
                }).fail(function () {
                    box.confirm("网络错误，是否刷新后重试", function (data) {
                        if (data)location.reload();
                    }, {
                        title: "网络错误",
                        value: "刷新页面"
                    })
                });
            return false;
        });

        $("#register_action").click(function () {
            var register_form = $("#register_template").html(),
                register_box = box.popup(register_form);
            $(register_box.find('input, textarea')).placeholder();
            register_box.find("#register_do").click(function () {
                if (!common.validate(register_box)) {
                    box.boxShake();
                    return false;
                }
                var params = {
                    _xsrf: xsrftoken,
                    action: 'register',
                    class_key :register_box.find("#class_key").val(),
                    email: register_box.find("#register_email").val(),
                    ccnu_id: register_box.find("#ccnu_id").val(),
                    password: register_box.find("#ccnu_psw").val()
                };
                box.boxClose();
                box.load("register");
                $.ajax({
                    type: "POST",
                    data: params,
                    url: "/account.do"
                }).done(function (data) {
                        if (data == "1") {
                            box.confirm("注册成功，立刻去登录", {
                                title: "注册成功",
                                value: "去登录"
                            })
                        } else {
                            box.alert("注册失败，请尝试稍后再次注册，如果仍不行可尝试更换邮箱", {
                                title: "注册失败"
                            })
                        }
                    }).always(function () {
                        box.ready("register");
                    }).fail(function () {
                        box.confirm("网络错误，是否刷新后重试", function (data) {
                            if (data)location.reload();
                        }, {
                            title: "网络错误",
                            value: "刷新页面"
                        })
                    });
                return false;
            });
            register_box.find("#register_cancel").click(function () {
                box.boxClose();
            });
            return false;
        });

        $("#password_action").click(function () {
            var password_form = $("#password_template").html(),
                password_box = box.popup(password_form);
            $(password_box.find('input, textarea')).placeholder();
            password_box.find("#password_do").click(function () {
                if (!common.validate(password_box)) {
                    box.boxShake();
                    return false;
                }
                var params = {
                    _xsrf: xsrftoken,
                    action: 'restPassword',
                    ccnu_id: password_box.find("#ccnu_id_rest").val(),
                    password: password_box.find("#ccnu_psw_rest").val()
                };
                box.boxClose();
                box.load("restPassword");
                $.ajax({
                    type: "POST",
                    data: params,
                    url: "/account.do"
                }).done(function (data) {
                        if (data == "1") {
                            box.confirm("密码重置成功，立刻去登录", {
                                title: "重置成功",
                                value: "去登录"
                            })
                        } else {
                            box.alert("重置失败，请核实帐号后再次重置", {
                                title: "重置失败"
                            })
                        }
                    }).always(function () {
                        box.ready("restPassword");
                    }).fail(function () {
                        box.confirm("网络错误，是否刷新后重试", function (data) {
                            if (data)location.reload();
                        }, {
                            title: "网络错误",
                            value: "刷新页面"
                        })
                    });
                return false;
            });
            password_box.find("#password_cancel").click(function () {
                box.boxClose();
            });
            return false;
        })

    });

    window.onload = function () {
        box.ready("page");
    };

}).call(window);