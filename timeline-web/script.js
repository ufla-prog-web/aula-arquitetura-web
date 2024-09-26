var navegadores = [
    [Date.UTC(1992,0,1), "Lynx"],
    [Date.UTC(1993,0,1), "Mosaic"],
    [Date.UTC(1994,0,1), "Netscape Navigator"],
    [Date.UTC(1995,0,1), "Internet Explorer"],
    [Date.UTC(1996,0,1), "Opera"],
    [Date.UTC(2003,0,1), "Safari"],
    [Date.UTC(2004,0,1), "Mozilla Firefox"],
    [Date.UTC(2008,0,1), "Google Chrome"],
    [Date.UTC(2015,0,1), "Microsoft Edge"],
];

var html = [
    [Date.UTC(1991,0,1), "HTML 1.0"],
    [Date.UTC(1995,0,1), "HTML 2.0"],
    [Date.UTC(1997,0,1), "HTML 3.2"],
    [Date.UTC(1997,5,1), "HTML 4.0"],
    [Date.UTC(1999,0,1), "HTML 4.01"],
    [Date.UTC(2014,0,1), "HTML 5.0"],
    [Date.UTC(2016,0,1), "HTML 5.1"],
    [Date.UTC(2017,0,1), "HTML 5.2"],
];

var css = [
    [Date.UTC(1996,0,1), "CSS 1.0"],
    [Date.UTC(1998,0,1), "CSS 2.0"],
    [Date.UTC(2004,0,1), "CSS 2.1"],
    [Date.UTC(2005,0,1), "CSS 3.0"],
];

var bootstrap = [
    [Date.UTC(2011,0,1), "Bootstrap 1.0"],
    [Date.UTC(2012,0,1), "Bootstrap 2.0"],
    [Date.UTC(2013,0,1), "Bootstrap 3.0"],
    [Date.UTC(2018,0,1), "Bootstrap 4.0"],
    [Date.UTC(2021,0,1), "Bootstrap 5.0"],
];

var javascript = [
    [Date.UTC(1995,0,1), "JavaScript 1.0"],
    [Date.UTC(1996,0,1), "JavaScript 1.1"],
    [Date.UTC(1997,0,1), "JavaScript 1.2"],
    [Date.UTC(1998,0,1), "JavaScript 1.3"],
    [Date.UTC(1999,0,1), "JavaScript 1.4"],
    [Date.UTC(2000,0,1), "JavaScript 1.5"],
];

var ecmascript = [
    [Date.UTC(1999,0,1), "ECMAScript 3"],
    [Date.UTC(2009,0,1), "ECMAScript 5"],
    [Date.UTC(2015,0,1), "ECMAScript 6"],
    [Date.UTC(2016,0,1), "ECMAScript 7"],
    [Date.UTC(2017,0,1), "ECMAScript 8"],
    [Date.UTC(2018,0,1), "ECMAScript 9"],
    [Date.UTC(2019,0,1), "ECMAScript 10"],
    [Date.UTC(2020,0,1), "ECMAScript 11"],
    [Date.UTC(2021,0,1), "ECMAScript 12"],
];

var http = [
    [Date.UTC(1991,0,1), "HTTP 0.9"],
    [Date.UTC(1996,0,1), "HTTP 1.0"],
    [Date.UTC(1997,0,1), "HTTP 1.1"],
    [Date.UTC(2015,0,1), "HTTP 2.0"],
];

var jquery = [
    [Date.UTC(2006,0,1), "jQuery 1.0"],
    [Date.UTC(2013,0,1), "jQuery 2.0"],
    [Date.UTC(2016,0,1), "jQuery 3.0"],
    [Date.UTC(2021,0,1), "jQuery 3.6"],
];

var django = [
    [Date.UTC(2008,0,1), "Django 1.0"],
    [Date.UTC(2017,0,1), "Django 2.0"],
    [Date.UTC(2019,0,1), "Django 3.0"],
    [Date.UTC(2021,0,1), "Django 4.0"],
    [Date.UTC(2023,0,1), "Django 5.0"],
];

var outros = [
    [Date.UTC(1994,0,1), "W3C"],
];

var php = [
    [Date.UTC(1995,0,1), "PHP 1.0"],
    [Date.UTC(1997,0,1), "PHP 2.0"],
    [Date.UTC(1998,0,1), "PHP 3.0"],
    [Date.UTC(2000,0,1), "PHP 4.0"],
    [Date.UTC(2004,0,1), "PHP 5.0"],
    [Date.UTC(2015,0,1), "PHP 7.0"],
    [Date.UTC(2020,0,1), "PHP 8.0"],
];


var chart = anychart.timeline();

var momentSeries2 = chart.moment(navegadores);

var momentSeries3 = chart.moment(html);

var momentSeries3 = chart.moment(css);

var momentSeries3 = chart.moment(bootstrap);

var momentSeries3 = chart.moment(javascript);

var momentSeries3 = chart.moment(ecmascript);

var momentSeries3 = chart.moment(http);

var momentSeries3 = chart.moment(jquery);

var momentSeries3 = chart.moment(django);

var momentSeries3 = chart.moment(php);

var momentSeries1 = chart.moment(outros);


// create two line markers
var lineMarker1 = chart.lineMarker(0);
var lineMarker2 = chart.lineMarker(1);
var lineMarker3 = chart.lineMarker(2);
var lineMarker4 = chart.lineMarker(3);

// set values of markers
lineMarker1.value(Date.UTC(1990,0,1));
lineMarker2.value(Date.UTC(2000,0,1));
lineMarker3.value(Date.UTC(2010,0,1));
lineMarker4.value(Date.UTC(2020,0,1));
lineMarker4.value(Date.UTC(2024,5,1));

// set the stroke of markers
lineMarker1.stroke("#00bfa5", 3, "10 5");
lineMarker2.stroke("#00bfa5", 3, "10 5");
lineMarker3.stroke("#00bfa5", 3, "10 5");
lineMarker4.stroke("#00bfa5", 3, "10 5");

chart.container("container");

chart.draw();
