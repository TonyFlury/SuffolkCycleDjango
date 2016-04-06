<!-- JQuery Magic to help the checkbox select/deselect all functions to work -->

    function TotalDistance() {
        // Calculate the Total Distance over all the selected Legs
        var _totalDistance = 0;

        // Look for each leg Row - and sum the distance cell to the total if the check is selected
        $.each( $('div.leg'), function(){
            if ($(this).children('div.check').children('input.RouteSelect').is(':checked') )
            {
                 _totalDistance += parseInt($(this).children('.km').text(), 10);
            };
        });

        // Dump the result to the totals box
        $('div#totalDistance').text(_totalDistance.toString());
    }

    function SyncSelectAll() {
        /* Count all of the legs, and all of those checke */
        var _total_legs = $('div.leg').length ;
        var _totalChecked = $('div.leg').children('div.check').children('input.RouteSelect:checked').length;

        TotalDistance();

        if(_totalChecked == _total_legs){
         $("input.selectAll").prop("checked", true);
        }else{
         $("input.selectAll").prop("checked", false);
        }
    }

$(document).ready(function(){

    // Bind a simple JQuery Function to ensure that SelectAll checkbox - set all boxes to the same state
    $('input.selectAll').bind( 'click', function(){
      $('input.RouteSelect').prop("checked", this.checked);
      TotalDistance();
    });

    //  ensure that the Selectall checkbox is kept in sync with the other checkboxes
    $('input.RouteSelect').bind( 'click', function() { SyncSelectAll() });

    SyncSelectAll(); // Synchronise selectAll and Total Distance for the first time
});