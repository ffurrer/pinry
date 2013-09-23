/**
 * Lightbox for Pinry
 * Descrip: A lightbox plugin for pinry so that I don't have to rely on some of
 *          the massive code bases of other lightboxes, this one uses data
 *          fields to acquire the info we need and dynamically loads comments.
 *          It also has a nice parallax view mode where the top scrolls and the
 *          background stays stationary.
 * Authors: Pinry Contributors
 * Updated: Feb 26th, 2013
 * Require: jQuery, Pinry JavaScript Helpers
 */

var createBox;


$(window).load(function() {
    // Start Helper Functions
    function freezeScroll(freeze) {
        freeze = typeof freeze !== 'undefined' ? freeze : true;
        if (freeze) {
            $('body').data('scroll-level', $(window).scrollTop());
            $('#pins').css({
                'position': 'fixed',
                'margin-top': -$('body').data('scroll-level')
            });
            $(window).scrollTop(0);
            /* disable the global pin-loading scroll handler so we don't
               load pins when scrolling a selected image */
            $(window).off('scroll');
        } else {
            $('#pins').css({
                'position': 'static',
                'margin-top': 0
            });
            $(window).scrollTop($('body').data('scroll-level'));
            /* enable the pin-loading scroll handler unless we've already
               loaded all pins from the server (in which case an element
               with id 'the-end' exists */
            var theEnd = document.getElementById('the-end');
            if (!theEnd) {
                $(window).scroll(scrollHandler);
            }
        }
    }
    // End Helper Functions


    // Start View Functions
    createBox = function(context) {
        freezeScroll();
        $('body').append(renderTemplate('#lightbox-template', context));
        var box = $('.lightbox-background');
        box.css('height', $(document).height());
        $('.lightbox-image-wrapper').css('height', context.image.standard.height);
        box.fadeIn(200);
        $('.lightbox-image').load(function() {
            $(this).fadeIn(200);
        });
        $('.lightbox-wrapper').css({
            'width': context.image.standard.width,
            'margin-top': 74,
            'margin-bottom': 70,
            'margin-left': -context.image.standard.width/2
        });
        if ($('.lightbox-wrapper').outerHeight(true) > $(window).height())
            $('.lightbox-background').height($('.lightbox-wrapper').outerHeight(true));

        box.click(function() {
            $(this).fadeOut(200);
            window.history.pushState("object or string", "Home", "/");
            setTimeout(function() {
                box.remove();
            }, 200);
            freezeScroll(false);
        });
        $('.lightbox-wrapper').click(function() {
            event.stopPropagation();
        });
        $('.dim.pinned').text(gettext('pinned by'));

        // Increase / decrease like count if like button clicked
        $('.lightbox-data .icon-like').click(function() {
            thisPin = $(this);
            backgroundPin = $('.pin-footer .icon-like[data-id='+$(this).data('id')+']');
            if ($(this).data('liked') == true) {
                var promise = unlikePin($(this).data('id'));
                // TODO: Change success() to done()
                promise.success(function(data) {
                    var likes = thisPin.data('like_count');
                    likes--;
                    thisPin.data('liked', false);
                    thisPin.removeClass('liked');
                    thisPin.data('like_count', likes);
                    thisPin.siblings('.like-count').text(likes);
                    backgroundPin.data('liked', false);
                    backgroundPin.data('like_count', likes);
                    backgroundPin.siblings('.like-count').text(likes);
                    backgroundPin.removeClass('liked');
                });
                promise.error(function() {
                    message(gettext('Problem unliking the pin.'), 'alert alert-error');
                });
            }
            else {
                var promise = likePin($(this).data('id'));
                promise.success(function(data) {
                    thisPin.data('liked', true);
                    thisPin.addClass('liked');
                    thisPin.data('like_count', data);
                    thisPin.siblings('.like-count').text(data);
                    backgroundPin.data('liked', true);
                    backgroundPin.data('like_count', data);
                    backgroundPin.siblings('.like-count').text(data);
                    backgroundPin.addClass('liked');
                });
                promise.error(function() {
                    message(gettext('Problem liking the pin.'), 'alert alert-error');
                });
            }
        });
    }
    // End View Functions

    // Start View Functions
    createInfoBox = function(context, width) {
        if (width === 'undefined') {
            width = 524;
        }
        freezeScroll();
        $('body').append(renderTemplate('#lightbox_container-template', context));
        var box = $('.lightbox-background');
        box.css('height', $(document).height());
        // $('.lightbox-image-wrapper').css('height', 634);
        box.fadeIn(200);
        // $('.lightbox-image').load(function() {
            // $(this).fadeIn(200);
        // });
        $('.lightbox-wrapper').css({
            'width': width,
            'margin-top': 74,
            'margin-bottom': 70,
            'margin-left': -width/2,
            'padding': 20
        });
        if ($('.lightbox-wrapper').outerHeight(true) > $(window).height())
            $('.lightbox-background').height($('.lightbox-wrapper').outerHeight(true));

        box.click(function() {
            $(this).fadeOut(200);
            setTimeout(function() {
                box.remove();
            }, 200);
            freezeScroll(false);
        });
        $('.lightbox-wrapper').click(function() {
            event.stopPropagation();
        });
    }
    // End View Functions


    // Start Global Init Function
    window.lightbox = function() {
        var links = $('body').find('.lightbox');
        return links.each(function() {
            $(this).off('click');
            $(this).click(function(e) {
                e.preventDefault();
                if ($(this).data('id') !== undefined) {
                    var promise = getPinData($(this).data('id'));

                    promise.success(function(pin) {
                        createBox(pin);
                        window.history.pushState("object or string", "Home", "/pin/" + pin.id);
                    });
                    promise.error(function() {
                        message(gettext('Problem fetching pin data.'), 'alert alert-error');
                    });
                }
                else {
                    var promise = getLightbox($(this).data('lightboxid'));
                    if ($(this).data('width') !== undefined) {
                        var lightboxWidth = $(this).data('width');
                    }
                    else {
                        var lightboxWidth = 800;
                    }
                    promise.success(function(data) {
                        createInfoBox(data, lightboxWidth);
                    });
                    promise.error(function() {
                        message(gettext('Problem fetching data.'), 'alert alert-error');
                    });
                }
            });
        });
    }
    // End Global Init Function
});
