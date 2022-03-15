$(".js-answer-correct").click(function (ev) {
    ev.preventDefault();
    const csrftoken = getCookie('csrftoken');
    const $this = $(this);

    $.ajax({
        method: "POST",
        url: "/answer_correct/",
        data: {'id': $this.data('id')},
        dataType: "json",
        headers: {'X-CSRFToken': csrftoken}
    }).always(function (data) {
        const errMsgId = 'is-right-answ-error-msg-';
        const $errMsg = $( '#' + errMsgId + $this.data('id'));
        $errMsg.hide();
        if (data.status === 'ok') {
            $this[0].checked ^= true;
        } else {
            if (!$errMsg.length) {
                $this.next().after('<div class="font-20 align-middle" id="' + errMsgId + $this.data('id') + '">Some error... Please try again</div>');
            }
            $errMsg.show();
        }
    });
})
