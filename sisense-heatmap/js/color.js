/* Utils - Color class */
(function(ns){

    // Tests the validity of a hex color string. Hex is considered valid both with or without the # character, and accepts both 6 and 3 character codes.
    function isValidHex(hex){
        if(typeof hex != 'string' || hex == null || hex.trim() == '')
            return false;
        return /^\#?[0-9a-fA-F]{6}$|^#?[0-9a-fA-F]{3}$/.test(hex)
    }

    // Color class constructor - can be created from hex or RGB
    function Color(hex){
        if(typeof hex == 'string' && isValidHex(hex)) {
            hex = hex.replace('#','');
            this.r = parseInt(hex.substr(0,2), 16);
            this.g = parseInt(hex.substr(2,2), 16);
            this.b = parseInt(hex.substr(4,2), 16);
        }
        else if(Array.isArray(hex) && hex.length == 3){
            this.r = hex[0];
            this.g = hex[1];
            this.b = hex[2];
        }
        else if(arguments.length == 3 && !isNaN(arguments[0]) && !isNaN(arguments[1]) && !isNaN(arguments[2])){
            this.r = arguments[0];
            this.g = arguments[1];
            this.b = arguments[2];
        }
        else {
            throw 'Invalid color';
        }
    }

    // Calculates the RGB delta between two colors
    Color.prototype.getDelta = function(color){
        return {
            r: this.r - color.r,
            g: this.g - color.g,
            b: this.b - color.b
        };
    }

    ns.Color = Color;
    ns.Color.isValidHex = isValidHex;

}(utils))