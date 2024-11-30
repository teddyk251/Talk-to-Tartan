window.mountChainlitWidget({
  // chainlitServer: "http://172.29.104.127:8000",
  chainlitServer: "http://localhost:8000",
});
  

window.addEventListener("chainlit-call-fn", (e) => {

  const { name, args, callback } = e.detail;

  if (name === "planUpdate") {
    
    console.log(name, args);

    dash_clientside.set_props("user-profile", {data: args.user_profile});

    // callback("You sent: " + JSON.stringify((args.user_profile)));
    callback("You sent: ");
  }
});