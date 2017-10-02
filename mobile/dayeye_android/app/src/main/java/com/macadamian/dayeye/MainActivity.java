package com.macadamian.dayeye;

import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.AsyncTask;
import android.support.annotation.NonNull;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;

import com.bumptech.glide.Glide;
import com.google.android.gms.auth.api.Auth;
import com.google.android.gms.auth.api.signin.GoogleSignInAccount;
import com.google.android.gms.auth.api.signin.GoogleSignInApi;
import com.google.android.gms.auth.api.signin.GoogleSignInOptions;
import com.google.android.gms.auth.api.signin.GoogleSignInResult;
import com.google.android.gms.common.ConnectionResult;
import com.google.android.gms.common.SignInButton;
import com.google.android.gms.common.api.GoogleApiClient;
import com.google.android.gms.common.api.ResultCallback;
import com.google.android.gms.common.api.Scope;
import com.google.android.gms.common.api.Status;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.Console;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.UnsupportedEncodingException;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLEncoder;
import java.util.HashMap;
import java.util.Map;

import javax.net.ssl.HttpsURLConnection;

import static android.R.attr.type;

public class MainActivity extends AppCompatActivity implements View.OnClickListener, GoogleApiClient.OnConnectionFailedListener {

    private static final String serverUrl = "http://172.24.10.63/dayeye/";
    private static final String PIServerUrl = "http://172.24.10.92:3000/face/";
    private static final String webClientId = "732334025518-n3k25bq7i5dukicc2oj0steuh61uj961.apps.googleusercontent.com";

    private LinearLayout ProfSection;
    private Button SignOut;
    private SignInButton SignIn;
    private Button StartFace;
    private TextView Name, Email, Counter;
    private ImageView ProfPic;

    private GoogleApiClient googleApiClient;

    private String storedEmail;

    private static final int REQ_CODE = 9001;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        ProfSection = (LinearLayout)findViewById(R.id.prof_selection);
        SignOut = (Button)findViewById(R.id.btn_logout);
        SignIn = (SignInButton)findViewById(R.id.btn_login);
        Name = (TextView)findViewById(R.id.name);
        Email = (TextView)findViewById(R.id.email);
        Counter = (TextView)findViewById(R.id.counter);
        ProfPic = (ImageView)findViewById(R.id.prof_pic);
        StartFace = (Button)findViewById(R.id.btn_start_recognition);

        SignIn.setOnClickListener(this);
        SignOut.setOnClickListener(this);
        StartFace.setOnClickListener(this);

        updateUI(false);

        GoogleSignInOptions signInOptions = new GoogleSignInOptions.Builder(GoogleSignInOptions.DEFAULT_SIGN_IN)
                .requestEmail()
                .requestScopes(new Scope("https://www.googleapis.com/auth/calendar.readonly"))
                .requestServerAuthCode(webClientId, false)
                .build();

        googleApiClient = new GoogleApiClient.Builder(this)
                .enableAutoManage(this, this)
                .addApi(Auth.GOOGLE_SIGN_IN_API, signInOptions)
                .build();


    }

    @Override
    public void onClick(View v) {

        switch (v.getId()) {
            case R.id.btn_login:
                signIn();
                break;
            case R.id.btn_logout:
                signOut();
                break;
            case R.id.btn_start_recognition:
                startRecognition(5);
                break;
        }
    }

    @Override
    public void onConnectionFailed(@NonNull ConnectionResult connectionResult) {

    }

    private void startRecognition(final int time) {

        if (time > 0) {
            StartFace.setVisibility(View.GONE);
            Counter.setVisibility(View.VISIBLE);
            runOnUiThread(new Runnable() {

                @Override
                public void run() {
                    Counter.setText(String.valueOf(time));
                }
            });
            new java.util.Timer().schedule(
                    new java.util.TimerTask() {
                        @Override
                        public void run() {
                            int decreaseTime = time - 1;
                            startRecognition(decreaseTime);
                        }
                    },
                    1000
            );
        }
        else {
            runOnUiThread(new Runnable() {

                @Override
                public void run() {
                    Counter.setText("Smile at the camera!");
                }
            });
            new java.util.Timer().schedule(
                    new java.util.TimerTask() {
                        @Override
                        public void run() {
                            runOnUiThread(new Runnable() {
                                @Override
                                public void run() {
                                    Counter.setText("Thank you!");
                                    new java.util.Timer().schedule(
                                            new java.util.TimerTask() {
                                                @Override
                                                public void run() {
                                                    runOnUiThread(new Runnable() {

                                                        @Override
                                                        public void run() {
                                                            updateUI(true);
                                                        }
                                                    });
                                                }
                                            },
                                            3000
                                    );
                                }
                            });
                        }
                    },
                    15000
            );
            final HashMap postData = new HashMap<>();
            postData.put("email", storedEmail);

            final String url = PIServerUrl + "register";

            doCall(url, postData);
        }
    }

    private void signIn(){
        Intent intent = Auth.GoogleSignInApi.getSignInIntent(googleApiClient);

        startActivityForResult(intent, REQ_CODE);
    }

    private void signOut(){
        Auth.GoogleSignInApi.signOut(googleApiClient).setResultCallback(new ResultCallback<Status>() {
            @Override
            public void onResult(@NonNull Status status) {
                updateUI(false);
            }
        });
    }

    private void handleResult(GoogleSignInResult result) {
        if(result.isSuccess()) {
            GoogleSignInAccount account = result.getSignInAccount();
            String first_name = account.getGivenName();
            String token = account.getServerAuthCode();
            String email = account.getEmail();
            String img_url = account.getPhotoUrl().toString();
//            img_url = "http://image.freepik.com/free-icon/facebook-logo-button_318-84980.jpg";
            storedEmail = email;
            sendToken(token, email, first_name);

            Name.setText(account.getDisplayName());
            Email.setText(email);

//            Glide.with(this)
//                    .load(img_url)
//                    .error(R.mipmap.ic_launcher)
//                    .into(ProfPic);
//            new DownloadImageTask(ProfPic)
//                    .execute(img_url);
            updateUI(true);
        }
        else {
            updateUI(false);
        }
    }

    private void updateUI(boolean isLogin) {
        Counter.setVisibility(View.GONE);
        if(isLogin) {
            StartFace.setVisibility(View.VISIBLE);
            ProfSection.setVisibility(View.VISIBLE);
            SignIn.setVisibility(View.GONE);
        }
        else {
            StartFace.setVisibility(View.GONE);
            ProfSection.setVisibility(View.GONE);
            SignIn.setVisibility(View.VISIBLE);
        }
    }


    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if(requestCode==REQ_CODE) {
            GoogleSignInResult result = Auth.GoogleSignInApi.getSignInResultFromIntent(data);
            handleResult(result);
        }
    }

    void sendToken(String token, String email, String first_name) {
        final HashMap postData = new HashMap<>();
        postData.put("Email", email);
        postData.put("FirstName", first_name);
        postData.put("AuthorizationToken", token);

        final String url = serverUrl + "login";

        doCall(url, postData);

    }

    private void doCall(final String url, final HashMap postData) {
        new AsyncTask<Void, Void, String>() {

            @Override
            protected String doInBackground(Void... params) {
                return performPostCall(url, postData);
            }
        }.execute();
    }

    public String  performPostCall(String requestURL,
                                   HashMap<String, String> postDataParams) {

        URL url;
        String response = "";
        try {
            url = new URL(requestURL);

            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setReadTimeout(15000);
            conn.setConnectTimeout(15000);
            conn.setRequestMethod("POST");
            conn.setDoInput(true);
            conn.setDoOutput(true);


            OutputStream os = conn.getOutputStream();
            BufferedWriter writer = new BufferedWriter(
                    new OutputStreamWriter(os, "UTF-8"));
            writer.write(getPostDataString(postDataParams));

            writer.flush();
            writer.close();
            os.close();
            int responseCode=conn.getResponseCode();

            if (responseCode == HttpsURLConnection.HTTP_OK) {
                String line;
                BufferedReader br=new BufferedReader(new InputStreamReader(conn.getInputStream()));
                while ((line=br.readLine()) != null) {
                    response+=line;
                }
            }
            else {
                response="";

            }
        } catch (Exception e) {
            e.printStackTrace();
        }

        return response;
    }
    private String getPostDataString(HashMap<String, String> params) throws UnsupportedEncodingException {
        StringBuilder result = new StringBuilder();
        boolean first = true;
        for(Map.Entry<String, String> entry : params.entrySet()){
            if (first)
                first = false;
            else
                result.append("&");

            result.append(URLEncoder.encode(entry.getKey(), "UTF-8"));
            result.append("=");
            result.append(URLEncoder.encode(entry.getValue(), "UTF-8"));
        }

        return result.toString();
    }


}

