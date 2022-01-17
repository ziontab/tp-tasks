$(".js-vote-answer").click(function (ev) {
    const csrftoken = getCookie('csrftoken');
    const $this = $(this);
    let action;
    if ($this.attr('id') === 'like-answer-' + $this.data('id')) {
        action = "like";
    } else {
        action = "dislike";
    }
    $.ajax({
        method: "POST",
        url: "/answer_vote/",
        data: {'id': $this.data('id'), 'action': action},
        dataType: "json",
        headers: {'X-CSRFToken': csrftoken}
    }).always(function (data) {
        const errMsgId = 'answer-vote-error-msg-';
        const $errMsg = $('#' + errMsgId + $this.data('id'));
        const $rating = $("#rating-answer-" + $this.data('id'))
        $errMsg.hide();
        if (data.status !== 'ok') {
            if (!$errMsg.length) {
                $rating.after('<div class="text-center w-100 " id="answer-vote-error-msg-' + $this.data('id') + '">' + data.message + '</div>');
            }
            $errMsg.text(data.message)
            $errMsg.show();
        } else {
            $rating.text(data.new_rating);
        }
    });
})
