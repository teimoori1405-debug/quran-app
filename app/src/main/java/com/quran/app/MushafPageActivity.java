package com.quran.app;
import android.graphics.Color;
import android.widget.ImageButton;
import android.content.SharedPreferences;

import android.app.Activity;
import android.os.Bundle;
import android.graphics.Typeface;
import android.content.res.AssetManager;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.MotionEvent;
import android.view.View;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import com.quran.app.data.MushafPageRepository;
import com.quran.app.data.MushafPageRepository.AyahItem;

import java.util.List;

public class MushafPageActivity extends Activity {

    private MushafPageRepository repository;
    private int pageNumber = 1;
    private boolean darkMode;
    private SharedPreferences preferences;

    private static final int LIGHT_BACKGROUND = Color.rgb(250, 250, 250);
    private static final int LIGHT_TEXT = Color.rgb(25, 25, 25);
    private static final int DARK_BACKGROUND = Color.BLACK;
    private static final int DARK_TEXT = Color.WHITE;

    private float downX;
    private float downY;

    private static final int SWIPE_THRESHOLD = 120;

    private Typeface quranFont;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        preferences = getSharedPreferences("quran_settings", MODE_PRIVATE);
        darkMode = preferences.getBoolean("dark_mode", false);

        pageNumber = getIntent().getIntExtra(
            "page_number",
            1
        );

        if (pageNumber < 1) pageNumber = 1;
        if (pageNumber > 604) pageNumber = 604;

        repository = new MushafPageRepository(this);

        try {
            quranFont = Typeface.createFromAsset(
                getAssets(),
                "fonts/AmiriQuran.ttf"
            );
        } catch (Exception e) {
            quranFont = Typeface.DEFAULT;
        }

        showPage();
    }

    private void showPage() {

        List<AyahItem> ayahs =
            repository.getPage(pageNumber);

        LinearLayout root =
            new LinearLayout(this);

        int backgroundColor = darkMode ? DARK_BACKGROUND : LIGHT_BACKGROUND;
        int textColor = darkMode ? DARK_TEXT : LIGHT_TEXT;

        root.setOrientation(
            LinearLayout.VERTICAL
        );

        root.setPadding(
            12,
            8,
            12,
            8
        );
        root.setBackgroundColor(backgroundColor);

        TextView pageTitle =
            new TextView(this);

        pageTitle.setText(
            "صفحه " +
            pageNumber +
            " از ۶۰۴"
        );

        pageTitle.setTextSize(
            TypedValue.COMPLEX_UNIT_SP,
            15
        );

        pageTitle.setGravity(
            Gravity.CENTER
        );

        pageTitle.setTypeface(
            Typeface.DEFAULT_BOLD
        );

        pageTitle.setTextColor(textColor);
        pageTitle.setPadding(
            0,
            2,
            0,
            6
        );

        root.addView(pageTitle);

        ImageButton themeButton = new ImageButton(this);
        themeButton.setImageResource(
            darkMode ? getResources().getIdentifier("ic_light_mode", "drawable", getPackageName()) : getResources().getIdentifier("ic_dark_mode", "drawable", getPackageName())
        );
        themeButton.setContentDescription(
            darkMode ? "حالت روشن" : "حالت تاریک"
        );
        themeButton.setBackgroundColor(android.graphics.Color.TRANSPARENT);
        themeButton.setOnClickListener(v -> {
            darkMode = !darkMode;
            preferences.edit().putBoolean("dark_mode", darkMode).apply();
            showPage();
        });

        LinearLayout.LayoutParams themeParams =
            new LinearLayout.LayoutParams(
                56,
                56
            );
        themeParams.gravity = Gravity.CENTER_HORIZONTAL;
        root.addView(themeButton, themeParams);


        MushafScrollView scrollView =
            new MushafScrollView(this);

        scrollView.setFillViewport(true);

        LinearLayout content =
            new LinearLayout(this);

        content.setOrientation(
            LinearLayout.VERTICAL
        );

        content.setPadding(
            6,
            10,
            6,
            30
        );

        int lastSurahNumber = -1;

        for (AyahItem ayah : ayahs) {

            if (ayah.surahNumber != lastSurahNumber) {

                TextView surahTitle =
                    new TextView(this);

                surahTitle.setText(
                    "سوره " +
                    ayah.surahName
                );

                surahTitle.setTextSize(
                    TypedValue.COMPLEX_UNIT_SP,
                    20
                );

                surahTitle.setGravity(
                    Gravity.CENTER
                );

                surahTitle.setTypeface(
                    Typeface.DEFAULT_BOLD
                );

                surahTitle.setTextColor(textColor);
                surahTitle.setTextDirection(
                    View.TEXT_DIRECTION_RTL
                );

                surahTitle.setPadding(
                    0,
                    14,
                    0,
                    14
                );

                content.addView(
                    surahTitle
                );

                lastSurahNumber =
                    ayah.surahNumber;
            }

            TextView ayahText =
                new TextView(this);

            ayahText.setText(
                ayah.text +
                " ﴿" +
                ayah.ayahNumber +
                "﴾"
            );
            ayahText.setTextColor(textColor);

            ayahText.setGravity(
                Gravity.RIGHT
            );

            ayahText.setTextDirection(
                View.TEXT_DIRECTION_RTL
            );

            ayahText.setIncludeFontPadding(
                true
            );

            ayahText.setLineSpacing(
                14,
                1.05f
            );

            ayahText.setPadding(
                0,
                8,
                0,
                12
            );

            ayahText.setTypeface(quranFont);

            ayahText.setTextSize(
                TypedValue.COMPLEX_UNIT_SP,
                27
            );

            content.addView(
                ayahText
            );
        }

        scrollView.addView(content);

        LinearLayout.LayoutParams scrollParams =
            new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                0,
                1
            );

        root.addView(
            scrollView,
            scrollParams
        );

        setContentView(root);

        scrollView.setOnTouchListener(
            (v, event) -> {

                switch (event.getActionMasked()) {

                    case MotionEvent.ACTION_DOWN:
                        downX = event.getX();
                        downY = event.getY();
                        return false;

                    case MotionEvent.ACTION_UP:

                        float deltaX =
                            event.getX() - downX;

                        float deltaY =
                            event.getY() - downY;

                        if (
                            Math.abs(deltaX) >
                            SWIPE_THRESHOLD &&
                            Math.abs(deltaX) >
                            Math.abs(deltaY)
                        ) {

                            if (deltaX > 0) {
                                nextPage();
                            } else {
                                previousPage();
                            }

                            return true;
                        }

                        return false;

                    default:
                        return false;
                }
            }
        );
    }

    private void nextPage() {

        if (pageNumber < 604) {
            pageNumber++;
            showPage();
        }
    }

    private void previousPage() {

        if (pageNumber > 1) {
            pageNumber--;
            showPage();
        }
    }

    private static class MushafScrollView
        extends ScrollView {

        private float startX;
        private float startY;

        public MushafScrollView(
            android.content.Context context
        ) {
            super(context);
        }

        @Override
        public boolean onInterceptTouchEvent(
            MotionEvent event
        ) {

            switch (event.getActionMasked()) {

                case MotionEvent.ACTION_DOWN:
                    startX = event.getX();
                    startY = event.getY();
                    break;

                case MotionEvent.ACTION_MOVE:

                    float dx =
                        Math.abs(event.getX() - startX);

                    float dy =
                        Math.abs(event.getY() - startY);

                    if (dx > dy && dx > 20) {
                        return true;
                    }

                    break;
            }

            return super.onInterceptTouchEvent(event);
        }
    }
}
