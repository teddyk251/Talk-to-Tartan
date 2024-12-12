
window.dash_clientside = Object.assign({}, window.dash_clientside, {
    
    clientside: {
        theme_switcher_callback: function (n_clicks) {
            let lightIcon = {'props': {'icon': 'ic:baseline-light-mode', 'width': 20, 'color':'gold'}, 'type': 'DashIconify', 'namespace': 'dash_iconify'}
            let darkIcon = {'props': {'icon': 'ic:sharp-dark-mode', 'width': 20, 'color':'#e8e3e6'}, 'type': 'DashIconify', 'namespace': 'dash_iconify'}
            let custom_theme_colors = {
                "dark_blue": ["#4A5468","#465064","#424C60","#3E485B","#3A4457","#354053","#313C4F","#2D384A","#293446","#253042"],
                "dimmed_purple":[ "#F5F2F6","#E6DEEA", "#DAC9E1", "#CFB3DB", "#C1A6CD", "#B39ABE", "#A790B0", "#9A87A3","#8F7E96","#85778B" ]
               }
            let lightColorScheme =  { 
                "fontFamily": "'Roboto','Arial',sans-serif",
                "colorScheme": "light",
                "colors":custom_theme_colors,
        
                "shadows": {
                    "xs": "0px 4px 3px -3px rgba(0, 0, 0, 0.05)",
                    "xl": "inset 0px 4px 3px -3px rgba(0, 0, 0, 0.05)",
                },
                "components": {

                },
            }
            let darktColorScheme =  { 
                "colorScheme": "dark",
                "fontFamily": "'YouTube Sans','Roboto',sans-serif",
                "colors": custom_theme_colors,
                "components": {
                    
                },
                "shadows": {
               
                    "xs": "0px 4px 3px -3px rgba(66, 66, 66, 1)",
                    "xl": "inset 0px 4px 3px -3px rgba(66, 66, 66, 1)",
                }
            }
            if (n_clicks % 2 === 0) { 
                
                document.documentElement.style.setProperty('--aside-bg-color', 'rgb(248, 246, 246)');

                return [ darktColorScheme, 'dark', lightIcon, 'Light']
              } 
              document.documentElement.style.setProperty('--aside-bg-color', 'rgb(31, 31, 31)');
          
        return [lightColorScheme, 'light', darkIcon, 'Dark']
        },

        side_bar_toggle: function (opened, navbar) {
            navbar["collapsed"] = {"mobile":  !opened}
            
        return navbar
        },
  
    },
});