      let map;
      let markers = [];

      function initMap() {
        map = new google.maps.Map(document.getElementById('map'), {
          center: {lat: 43.6211955, lng: -84.6824346},
          zoom: 0
        });
          
        let locations = [
          {title: 'Bowl One Lanes', location: {lat: 42.53459279, lng: -83.0953341}, address: '1639 E 14 Mile Rd, Troy, MI 48083', phonenumber: '(248)-588-4850', site: 'https://bowldetroit.com/bowl-one/'},
            
          {title: 'Luxury Lanes', location: {lat: 42.4603541, lng: -83.1256903}, address: '600 E 9 Mile Rd, Ferndale, MI 48220', phonenumber: '(248)-544-0530', site: 'https://luxurylanes16.com'},
            
          {title: 'Ford Lanes', location: {lat: 42.26991535, lng: -83.25923877}, address: '23100 Van Born Rd, Dearborn Heights, MI 48125', phonenumber: '(313)-292-1700', site: 'https://fordlanes.com'},
            
          {title: 'Oak Lanes', location: {lat: 42.3414471, lng: -83.3316437}, address: '8450 North Middlebelt Rd, Westland, MI 48185', phonenumber: '(734)-422-7420', site: 'http://oaklanesbowlingcenter.com'},
            
          {title: 'Five Star Lanes', location: {lat: 42.56254625, lng: -83.08166731}, address: '2666 Metropolitan Pkwy, Sterling Heights, MI 48310', phonenumber: '(586)-939-2550', site: 'http://www.fivestarlanes.com'},
            
          {title: 'Brighton Bowl', location: {lat: 42.52275639, lng: -83.76685856}, address: '9871 E Grand River Ave, Brighton, MI 48116', phonenumber: '(810) 227-3341', site: 'https://brightonbowl.com'},
            
          {title: 'Merri-Bowl Lanes', location: {lat: 42.39782489, lng: -83.35011048}, address: '30950 5 Mile Rd, Livonia, MI 48154', phonenumber: '(734)-427-2900', site: 'https://merribowl.com'},
            
          {title: 'Plum Hollow Lanes', location: {lat: 42.4585696, lng: -83.2294983}, address: '21900 W 9 Mile Rd, Southfield, MI 48075', phonenumber: '(248)-353-6540', site: 'https://bowldetroit.com/plum-hollow/'},   
            
          {title: 'Bel-Mark Lanes', location: {lat: 42.2849637, lng: -83.8004786}, address: '3530 Jackson Rd, Ann Arbor, MI 48103', phonenumber: '(734)-994-8433', site: 'https://www.belmarklanes.com'},  
            
          {title: 'Perfect Game Bowling', location: {lat: 42.4683201, lng: -83.4198687}, address: '35000 Grand River Ave., Farmington Hills MI 48335', phonenumber: '(248)-478-2230', site: 'https://myperfectgame.com'}, 
            
          {title: 'Alley 59', location: {lat: 42.62717042, lng: -82.8766906}, address: '44925 N Groesbeck Hwy, Clinton Township, MI 48036', phonenumber: '(586)-469-6411', site: 'http://alley59.com'},
            
          {title: 'Pinz Bowling Center', location: {lat: 42.56319583, lng: -83.34228516}, address: '700 N. Lafayette, South Lyon, MI 48178', phonenumber: '(248)-437-0700', site: 'https://pinzsouthlyon.com'},
            
          {title: 'The Voyageur', location: {lat: 42.8217204, lng: -82.4861555}, address: '525 S. Riverside Ave, Saint Clair, MI 48079', phonenumber: '(810)-329-3331', site: 'https://www.thevoyageur.com'},     
        ];

        let largeInfowindow = new google.maps.InfoWindow();
        let bounds = new google.maps.LatLngBounds();

        for (let i = 0; i < locations.length; i++) {
          let position = locations[i].location;
          let title = locations[i].title;
          let address = locations[i].address;  
          let phonenumber = locations[i].phonenumber;
          let site = locations[i].site;    
          let marker = new google.maps.Marker({
            map: map,
            position: position,
            title: title,
            address: address, 
            phonenumber: phonenumber,
            site: site,
            animation: google.maps.Animation.DROP,
            id: i
          });
          markers.push(marker);
          marker.addListener('click', function() {
            populateInfoWindow(this, largeInfowindow);
          });
          bounds.extend(markers[i].position);
        }
        map.fitBounds(bounds);
      }

      function populateInfoWindow(marker, infowindow) {
        if (infowindow.marker != marker) {
          infowindow.marker = marker;
          infowindow.setContent(`<div class="font-weight-bolder text-center"> <h3> ${marker.title}</h3> <br> <address> ${marker.address} </address>  Website: <a href="${marker.site}" title="${marker.title} website" target="_blank">${marker.title}</a> <br><br> <p> <a href="https://www.google.com/search?safe=active&ei=ySDNW4TuKsizggeag46wBw&q=${marker.title}" target="_blank" title="Google search for ${marker.title}!"><i class="fab fa-google fa-2x"></i></a></p> <p> <i class="fas fa-phone-alt"></i> ${marker.phonenumber}</p> </div>`);
          infowindow.open(map, marker);
          infowindow.addListener('closeclick',function(){
            infowindow.setMarker = null;
          });
        }
      }