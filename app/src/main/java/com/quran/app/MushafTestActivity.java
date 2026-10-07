package com.quran.app;

import android.app.Activity;
import android.os.Bundle;
import android.content.Intent;

public class MushafTestActivity extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        Intent intent =
            new Intent(this, MushafPageActivity.class);

        intent.putExtra("page_number", 1);

        startActivity(intent);
        finish();
    }
}
