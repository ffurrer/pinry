/**
 * Pinry
 * Descrip: Core of pinry, loads and tiles pins.
 * Authors: Pinry Contributors
 * Updated: Apr 5th, 2013
 * Require: jQuery, Pinry JavaScript Helpers
 */
sorting_order = '';

$(window).load(function() {
    /**
     * tileLayout will simply tile/retile the block/pin container when run. This
     * was put into a function in order to adjust frequently on screen size 
     * changes.
     */
    window.tileLayout = function() {
        var blockContainer = $('#pins'),
            blocks = blockContainer.children('.pin'),
            blockMargin = 15,
            blockWidth = 240,
            rowSize = Math.floor(blockContainer.width()/(blockWidth+blockMargin)),
            colHeights = [],
            rowMargins = [],
            marginLeft = 0;

        // Fill our colHeights array with 0 for each row we have
        for (var i=0; i < rowSize; i++) colHeights[i] = 0;
        // Fill out our rowMargins which will be static after this
        for (var i=0; i < rowSize; i++) {
            // Our first item has a special margin to keep things centered
            if (i == 0) rowMargins[0] = (blockContainer.width()-rowSize*(blockWidth+blockMargin))/2;
            else rowMargins[i] = rowMargins[i-1]+(blockWidth+blockMargin);
        }
        // Loop through every block
        for (var b=0; b < blocks.length; b++) {
            // Get the jQuery object of the current block
            block = blocks.eq(b);
            // Position our new pin in the shortest column
            var sCol = 0;
            for (var i=0; i < rowSize; i++) {
                if (colHeights[sCol] > colHeights[i]) sCol = i;
            }
            block.css({
                'margin-left': rowMargins[sCol],
                'margin-top':  colHeights[sCol],
            });
            block.fadeIn(300);
            colHeights[sCol] += block.height()+(blockMargin);
        }

        // Edit pin if pencil icon clicked
        $('.icon-pencil').each(function() {
            var thisPin = $(this);
            // $(this).off('click');
            $(this).click(function() {
                // $(this).off('click');
                pinForm($(this).data('id'));
                $('.new-pin').text(gettext('Edit Pin'));
                $('#pin-form-submit').text(gettext('Post'));
            });
        });

        // Delete pin if trash icon clicked
        $('.icon-trash').each(function() {
            $(this).off('click');
            $(this).click(function() {
                yesnodialog(gettext('Yes'), gettext('No'), $(this));
            });
        });

        if (currentUser.username !== "") {
            // Increase / decrease like count if like button clicked
            $('.icon-like').each(function() {
                var thisPin = $(this);
                $(this).off('click');
                $(this).click(function() {
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
                        });
                        promise.error(function() {
                            message(gettext('Problem unliking the pin.'), 'alert alert-error');
                        });
                    }
                    else {
                        var promise = likePin($(this).data('id'));
                        promise.success(function(data) {
                            thisPin.data('liked', true);
                            thisPin.data('like_count', data);
                            thisPin.addClass('liked');
                            thisPin.siblings('.like-count').text(data);
                        });
                        promise.error(function() {
                            message(gettext('Problem liking the pin.'), 'alert alert-error');
                        });
                    }
                });
            });
        }
        else {
            $('.icon-like').hover(
                function () {
                    elem = $(this);
                    elem.css('cursor', 'default');
                    elem.attr('title',gettext('You need to be logged in to like this pin.'));
                },
                function() {
                    $(this).css('cursor', 'default');
                }
            );
        }

        // Show edit-buttons only on mouse over
        $('.pin').each(function(){
            var thisPin = $(this);
            thisPin.find('.editable').hide();
            thisPin.off('hover');
            thisPin.hover(function() {
                thisPin.find('.editable').stop(true, true).fadeIn(300);
            }, function() {
                thisPin.find('.editable').stop(true, false).fadeOut(300);
            });
        });

        $('.spinner').css('display', 'none');
        blockContainer.css('height', colHeights.sort(function(a,b) {
            return a - b;
        }).slice(-1)[0]);
        $('.dim.pinned').text(gettext('pinned by'));
    }

    /**
     * On scroll load more pins from the server
     */
    window.scrollHandler = function() {
        var windowPosition = $(window).scrollTop() + $(window).height();
        var bottom = $(document).height() - 100;
        if(windowPosition > bottom) loadPins(sorting_order);
    }
    basicPins = [];
    function loadBasicPins(amount) {
        var apiUrl = '/api/v1/pin/?format=json&order_by=id&limit='+amount;
        $.get(apiUrl, function(pins) {
            basicPins = pins;
        });
    }
    /**
     * Load our pins using the pins template into our UI, be sure to define a
     * offset outside the function to keep a running tally of your location.
     */
    function loadPins(order, requester_only) {
        if (typeof order === 'undefined') {
            order = "like_count";
        }
        sorting_order = order;
        if (typeof requester_only === 'undefined') {
            requester_only = false;
        }
        // Disable scroll
        $(window).off('scroll');

        // Show our loading symbol
        $('.spinner').css('display', 'block');

        // Fetch our pins from the api using our current offset
        var apiUrl = '/api/v1/pin/?format=json&order_by='+order+'&offset='+String(offset);

        if (tagFilter) {
            apiUrl = apiUrl + '&tag=' + tagFilter;
            $('#sorter-date').removeClass('active');
            $('#sorter-mine').removeClass('active');
            $('#sorter-likes').removeClass('active');
        }
        if (userFilter) {
            apiUrl = apiUrl + '&submitter__username=' + userFilter;
            $('#sorter-date').removeClass('active');
            $('#sorter-mine').removeClass('active');
            $('#sorter-likes').removeClass('active');
        }
        if (requester_only && !userFilter) apiUrl = apiUrl + '&submitter__username=' + currentUser.username;

        $.get(apiUrl, function(pins) {
            var a = Math.floor(Math.random()*insertNSpecial);
            for (var i=0; i < pins.objects.length; i++){
                //get rid of special pins, that are already in the list
                if (pins.objects[i].link) {
                    pins.objects.splice(i,1);
                    i-=1;
                    continue;
                }
                // insert special pins at every insertSpecialEveryN position
                if (i%insertSpecialEveryN == (insertSpecialEveryN-1) && i < pins.objects.length -1) {
                    pins.objects.splice(i,0,basicPins.objects[a%insertNSpecial]);
                    i+=1;
                    a +=1;
                }
                // Set which items are editable by the current user
                pins.objects[i].editable = (pins.objects[i].submitter.username == currentUser.username);
            }




            // Use the fetched pins as our context for our pins template
            var template = Handlebars.compile($('#pins-template').html());
            var html = template({pins: pins.objects});

            // Append the newly compiled data to our container
            $('#pins').append(html);

            // We need to then wait for images to load in and then tile
            tileLayout();
            if (pinFilter) {
                var promise = getPinData(pinFilter);
                promise.success(function(pin) {
                    createBox(pin);
                    window.history.pushState("object or string", "Home", "/pin/" + pin.id);
                    // tileLayout();
                });
                promise.error(function() {
                    message(gettext('Problem fetching pin data.'), 'alert alert-error');
                });
            }
            lightbox();
            $('#pins').ajaxStop(function() {
                $('img').load(function() {
                    $(this).fadeIn(300);
                });
            });

            if (pins.objects.length < apiLimitPerPage) {
                $('.spinner').css('display', 'none');
                if ($('#pins').length != 0) {
                    var theEnd = document.createElement('div');
                    theEnd.id = 'the-end';
                    $(theEnd).html('&mdash; ' + gettext('End') + ' &mdash;');
                    $(theEnd).css('padding', 50);
                    $('body').append(theEnd);
                }
            } else {
                $(window).scroll(scrollHandler);
            }
        });

        // Up our offset, it's currently defined as 50 in our settings
        offset += apiLimitPerPage;
        $('.dim.pinned').text(gettext('pinned by'));
    }

    function yesnodialog(button1, button2, element){
      var btns = {};
      var thisPin = element;
      btns[button1] = function(){
            element.off('click');
            var promise = deletePinData(element.data('id'));
            promise.success(function() {
                thisPin.closest('.pin').remove();
                tileLayout();
            });
            promise.error(function() {
                message(gettext('Problem deleting image.'), 'alert alert-error');
            });

            $(this).dialog("close");
      };
      btns[button2] = function(){ 
          // Do nothing
          $(this).dialog("close");
      };
      $("<div><p>" + gettext('Do you really want to delete this pin?') + "</p></div>").dialog({
        autoOpen: true,
        title: gettext('Delete Pin?'),
        modal:true,
        buttons:btns
      });
    }    

    /**
     * Load our brandpartners using the brandpartner template 
     * into our bottom navigation.
     */
    function loadBrandpartner(start) {
        if (typeof start === 'undefined') {
            start = 0;
        }

        // Fetch our brandpartner from the api starting at start
        var apiUrl = '/api/v1/lightbox/?format=json&offset='+String(start);

        $.get(apiUrl, function(brandpartners) {

            // Use the fetched pins as our context for our pins template
            var template = Handlebars.compile($('#brandpartner-template').html());
            var html = template({brandpartners: brandpartners.objects});

            // Append the newly compiled data to our container
            $('#brandpartners').append(html);

            $('#brandpartners').ajaxStop(function() {
                $('img').load(function() {
                    $(this).fadeIn(300);
                });
            });
        });
    }


    // Set offset for loadPins and do our initial load
    var offset = 0;
    var insertSpecialEveryN = 3;
    var insertNSpecial = 25;
    loadBasicPins(insertNSpecial);
    loadPins('-like_count');
    loadBrandpartner(0);

    // If our window gets resized keep the tiles looking clean and in our window
    $(window).resize(function() {
        tileLayout();
        lightbox();
    })
    // Sorting according the most likes
    $('#sorter-likes').click(function() {
        toggleSorterClass($(this));
        sortPins('-like_count');
    });

    // Sorting according to the most recent uploads
    $('#sorter-date').click(function() {
        toggleSorterClass($(this));
        sortPins('-published');
    });

    // Show only user's pins
    $('#sorter-mine').click(function() {
        toggleSorterClass($(this));
        sortPins('-published', true);
    });

    $("#login_button").hover(function(){
        $("#fb-logo").css("background-image", 'url("../static/img/facebook_f_iv.png")');
        },function(){
        $("#fb-logo").css("background-image", 'url("../static/img/facebook_f.png")');
    });
    

    function sortPins(order, requester_only) {
        offset = 0;
        $('#the-end').remove();
        $('#pins').empty();
        loadPins(order, requester_only);
    }

    function toggleSorterClass(elem) {
        userFilter = false;
        tagFilter = false;
        pinFilter = false;
        window.history.pushState("object or string", "Home", "/");
        $('#sorter-date').removeClass('active');
        $('#sorter-mine').removeClass('active');
        $('#sorter-likes').removeClass('active');
        elem.addClass('active');
    }

});


