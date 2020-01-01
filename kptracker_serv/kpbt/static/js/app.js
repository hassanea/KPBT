/* app.js file */


/* Search funcrionality - Centers Home */
$(document).ready(function () {
        $("#center-search").on("keyup", function () {
            var value = $(this).val().toLowerCase();
            $("#centers-table tr").filter(function () {
                $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
            });
        });
    });

/* Search funcrionality - Leagues Home */
$(document).ready(function () {
        $("#league-search").on("keyup", function () {
            var value = $(this).val().toLowerCase();
            $("#leagues-table tr").filter(function () {
                $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
            });
        });
    });

/* Search funcrionality - Teams Home */
$(document).ready(function () {
        $("#team-search").on("keyup", function () {
            var value = $(this).val().toLowerCase();
            $("#teams-table tr").filter(function () {
                $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
            });
        });
    });

/* Tooltips */   
$(document).ready(function(){
  $('[data-toggle="tooltip"]').tooltip();   
});