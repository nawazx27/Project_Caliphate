/* Version 508: the parts of d3 7.9 the atlas uses. Rebuild src/vendor/d3custom.min.js after changing this list:
   NODE_PATH=node_modules node_modules/.bin/esbuild src/vendor/d3_entry.js --bundle --minify --format=iife --global-name=d3 --outfile=src/vendor/d3custom.min.js
   (check src/*.js with  grep -o "d3\.[a-zA-Z]*" src/*.js | sort -u  first: every d3.x the page uses must be exported here) */
export {select, selectAll, pointer} from 'd3-selection';
import 'd3-transition';
export {zoom, zoomIdentity, zoomTransform} from 'd3-zoom';
export {geoMercator, geoPath, geoCircle} from 'd3-geo';
export {min} from 'd3-array';
