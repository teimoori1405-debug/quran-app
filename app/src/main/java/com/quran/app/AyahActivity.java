package com.quran.app;

import android.app.Activity;
import android.os.Bundle;
import android.widget.TextView;

public class AyahActivity extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        TextView text = new TextView(this);
        text.setText("آیات سوره");
        text.setTextSize(24);
        text.setPadding(24, 24, 24, 24);

        setContentView(text);
    }
}
