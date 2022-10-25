const dataTableInitComplete = function (settings, json) {
    // $("#loading").hide();
    const $this = $(this);
    // $this.show();
    $.SOW.core.ajax_modal.ajax_modal($this.find('.js-ajax-modal'));
    $.SOW.core.ajax_confirm.init('.js-ajax-confirm')
}
