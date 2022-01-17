$(".js-vote-question").click(function (ev) {
    const csrftoken = getCookie('csrftoken');
    const $this = $(this);
    let action;
    if ($this.attr('id') === 'like-question-' + $this.data('id')) {
        action = "like";
    } else {
        action = "dislike";
    }
    $.ajax({
        method: "POST",
        url: "/question_vote/",
        data: {'id': $this.data('id'), 'action': action},
        dataType: "json",
        headers: {'X-CSRFToken': csrftoken}
    }).always(function (data) {
        const errMsgId = 'question-vote-error-msg-';
        const $errMsg = $('#' + errMsgId + $this.data('id'));
        const $rating = $("#rating-question-" + $this.data('id'))
        $errMsg.hide();
        if (data.status !== 'ok') {
            if (!$errMsg.length) {
                $rating.after('<div class="text-center w-100 " id="question-vote-error-msg-' + $this.data('id') + '">' + data.message + '</div>');
            }
            $errMsg.text(data.message)
            $errMsg.show();
        } else {
            $rating.text(data.new_rating);
        }
    });
})
