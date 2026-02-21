import streamlit as st
import streamlit.components.v1 as components
import uuid

# API URL
API_URL = "http://localhost:8000/chat"

# Session
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Page config
st.set_page_config(
    page_title="Atlas Horizon Hotel customer assistant",
    layout="wide"
)

# ===============================
# SIDEBAR (UNCHANGED)
# ===============================

with st.sidebar:
    st.title("Guest Info")
    st.markdown("---")

    guest_type = st.selectbox(
        "Guest Type",
        ["Business", "Leisure", "Family", "Group", "VIP"],
        index=0
    )

    loyalty = st.selectbox(
        "Loyalty Tier",
        ["Bronze", "Silver", "Gold", "Platinum", "Diamond"],
        index=2
    )

    city = st.text_input("City", "Sydney")

    st.session_state.guest_info = {
        "guest_type": guest_type,
        "loyalty": loyalty,
        "city": city
    }

    st.markdown("---")
    st.write(f"Session ID: {st.session_state.session_id}")


# ===============================
# CHAT INTERFACE (HTML)
# ===============================

chat_html = f"""
<!DOCTYPE html>
<html>
<head>

<link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.1.1/css/bootstrap.min.css" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.5.0/css/all.css">

<style>

body,html{{
	height:70%;
	margin:0;
	background:rgba(0,0,0,0.4);
}}

.chat{{
	margin:auto;
}}

.card{{
	height:600px;
	border-radius:15px;
	background-color:rgba(0,0,0,0.9);
    border:2px solid #52acff;
}}

.msg_card_body{{
	overflow-y:auto;
}}

.type_msg{{
	background-color:rgba(0,0,0,0.3);
	border:0;
	color:whitesmoke;
	height:60px;
}}

.send_btn{{
	background-color:rgba(0,0,0,0.3);
	border:0;
	color:white;
}}

.msg_cotainer{{
	border-radius:25px;
	background-color:#52acff;
	padding:10px;
}}

.msg_cotainer_send{{
	border-radius:25px;
	background-color:#58cc71;
	padding:10px;
}}

.user_img{{
	height:60px;
	width:60px;
}}

.user_img_msg{{
	height:35px;
	width:35px;
}}
.user_info {{
    display:flex;
    flex-direction:column;
    justify-content:center;
    align-items:center;
    width:100%;
    text-align:center;
}}

.user_info span {{
    font-size:2em;
    font-weight:bold;
    font-spacing:5px;
}}


</style>

</head>

<body>

<div class="container-fluid h-100">
<div class="row justify-content-center h-100">

<div class="col-md-8 col-xl-6 chat">

<div class="card">

<div class="card-header">

<div class="d-flex bd-highlight">

<div class="user_info ml-3 text-white">
<span>Atlas Horizon customer support</span>
</div>

</div>
</div>


<div id="messageBody" class="card-body msg_card_body">
<!-- Initial greeting message -->
<div class="d-flex justify-content-start mb-3">
    <div class="msg_cotainer">
        Hi esteemed customer, how can I be of help today?
    </div>
</div>
</div>


<div class="card-footer">

<form id="chatForm" class="input-group">

<input type="text" id="msg" placeholder="Type your message..." class="form-control type_msg"/>

<div class="input-group-append">

<button class="input-group-text send_btn">
<i class="fas fa-location-arrow"></i>
</button>

</div>

</form>

</div>

</div>
</div>
</div>
</div>


<script>

// Scroll to bottom on page load to show the greeting
$(document).ready(function() {{
    $("#messageBody").scrollTop(
        $("#messageBody")[0].scrollHeight
    );
}});

$("#chatForm").on("submit", function(e){{
    e.preventDefault();

    let text = $("#msg").val();

    if(text.trim() === "") return;

    let userHtml = `
    <div class="d-flex justify-content-end mb-3">
        <div class="msg_cotainer_send">
            ${{text}}
        </div>
    </div>`;

    $("#messageBody").append(userHtml);
    $("#msg").val("");

    fetch("{API_URL}", {{
        method:"POST",
        headers:{{
            "Content-Type":"application/json"
        }},
        body:JSON.stringify({{
            question:text,
            session_id:"{st.session_state.session_id}",
            guest_type:"{st.session_state.guest_info['guest_type']}",
            loyalty:"{st.session_state.guest_info['loyalty']}",
            city:"{st.session_state.guest_info['city']}"
        }})
    }})

    .then(res => res.json())

    .then(data => {{

        let botHtml = `
        <div class="d-flex justify-content-start mb-3">
            <div class="msg_cotainer">
                ${{data.answer}}
            </div>
        </div>`;

        $("#messageBody").append(botHtml);

        $("#messageBody").scrollTop(
            $("#messageBody")[0].scrollHeight
        );

    }});

}});

</script>

</body>
</html>
"""

components.html(chat_html, height=700, scrolling=False)