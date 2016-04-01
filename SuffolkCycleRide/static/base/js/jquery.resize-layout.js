/*
 SuffolkCycleDjango : Implementation of jquery.resize-layout

Summary : 
   Automatically resize the key content divs to take into account client widths
Use Case : 
    As a User
    I want the layout to adjust as the browser window re-sizes
    So that the layout continues to be efficient, and does not force unreasonable horizontal scrolling.

Testable Statements :
    Can I <Boolean statement>
    ....
    
   version : 0.1
   author  : Tony Flury : anthony.flury@btinternet.com
   created : 17 Feb 2016
*/


function resetHeaderFooterWidths() {

    var content_width = 900 ; /* ****** DONOT Set to less than 900 ***** */
    var width = (window.innerWidth
                    || document.documentElement.clientWidth
                    || document.body.clientWidth) ;
    var gap ;

    if (width < 900)
        {
            gap = 0;
            content_width = width;
        }
    else
        {
            gap = ((width - content_width)/2) - 10;
            width = width - 25 ;
        }

    $('#Site_Background').css('width', (width).toString() + "px" );

    $.each( $('div#content'), function(){
            $( this ).css('width', content_width.toString()+"px");
    });

    $.each( $('.Site_Root'), function(){
            $( this ).css('width', content_width.toString()+"px");
            $( this ).css('margin-left', gap.toString() + "px");
            $( this ).css('margin-right', gap.toString() + "px");
    });

    $.each( $('#header'), function(){
            $( this ).css('width', content_width.toString()+"px");
    });

    $.each( $('#footer'), function(){
            $( this ).css('width', content_width.toString()+"px");
    });

    $.each( $('.strip'), function(){
            $( this).css('left', (-gap).toString() + "px" );
            $( this).css('width', (width).toString() + "px" );
        });

    $.each( $('#header_bg'), function(){
            $( this).css('left', (-gap).toString() + "px" );
            $( this).css('width', (width).toString() + "px" );
        });

    $.each( $('#footer_bg'), function (){
            $( this).css('left', (-gap).toString() + "px" );
            $( this).css('width', (width).toString() + "px" );
        });
}

$(document).ready(function(){
            resetHeaderFooterWidths();
        });

$(window).resize(function(){
            resetHeaderFooterWidths();
 });