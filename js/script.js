$(document).ready(function() {
    $('#resumeForm').on('submit', function(e) {
        let valid = true;
        $('input[required], textarea[required]').each(function() {
            if (!$(this).val().trim()) {
                valid = false;
                $(this).addClass('is-invalid');
            } else {
                $(this).removeClass('is-invalid');
            }
        });
        if (!valid) e.preventDefault();
    });
});