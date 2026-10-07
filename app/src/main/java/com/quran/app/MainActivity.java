package com.quran.app;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

public class MainActivity extends Activity {

    private static final String[] SURAHS = {
        "الفاتحة", "البقرة", "آل عمران", "النساء", "المائدة",
        "الأنعام", "الأعراف", "الأنفال", "التوبة", "يونس",
        "هود", "يوسف", "الرعد", "إبراهيم", "الحجر",
        "النحل", "الإسراء", "الكهف", "مريم", "طه",
        "الأنبياء", "الحج", "المؤمنون", "النور", "الفرقان",
        "الشعراء", "النمل", "القصص", "العنكبوت", "الروم",
        "لقمان", "السجدة", "الأحزاب", "سبأ", "فاطر",
        "يس", "الصافات", "ص", "الزمر", "غافر",
        "فصلت", "الشورى", "الزخرف", "الدخان", "الجاثية",
        "الأحقاف", "محمد", "الفتح", "الحجرات", "ق",
        "الذاريات", "الطور", "النجم", "القمر", "الرحمن",
        "الواقعة", "الحديد", "المجادلة", "الحشر", "الممتحنة",
        "الصف", "الجمعة", "المنافقون", "التغابن", "الطلاق",
        "التحريم", "الملك", "القلم", "الحاقة", "المعارج",
        "نوح", "الجن", "المزمل", "المدثر", "القيامة",
        "الإنسان", "المرسلات", "النبأ", "النازعات", "عبس",
        "التكوير", "الانفطار", "المطففين", "الانشقاق", "البروج",
        "الطارق", "الأعلى", "الغاشية", "الفجر", "البلد",
        "الشمس", "الليل", "الضحى", "الشرح", "التين",
        "العلق", "القدر", "البينة", "الزلزلة", "العاديات",
        "القارعة", "التكاثر", "العصر", "الهمزة", "الفيل",
        "قريش", "الماعون", "الكوثر", "الكافرون", "النصر",
        "المسد", "الإخلاص", "الفلق", "الناس"
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);

        TextView title = new TextView(this);
        title.setText("قرآن کریم");
        title.setTextSize(28);
        title.setPadding(24, 24, 24, 12);
        root.addView(title);

        TextView subtitle = new TextView(this);
        subtitle.setText("فهرست سوره‌ها");
        subtitle.setTextSize(18);
        subtitle.setPadding(24, 0, 24, 12);
        root.addView(subtitle);

        TextView mushafButton = new TextView(this);
        mushafButton.setText("نمایش مصحف — صفحه ۱");
        mushafButton.setTextSize(18);
        mushafButton.setPadding(24, 20, 24, 20);
        mushafButton.setGravity(android.view.Gravity.CENTER);
        mushafButton.setOnClickListener(v -> {
            startActivity(
                new android.content.Intent(this, MushafPageActivity.class)
                    .putExtra("page_number", 1)
            );
        });
        root.addView(mushafButton);

        String[] items = new String[SURAHS.length];

        for (int i = 0; i < SURAHS.length; i++) {
            items[i] = (i + 1) + ". " + SURAHS[i];
        }

        ListView listView = new ListView(this);

        ArrayAdapter<String> adapter = new ArrayAdapter<String>(
            this,
            android.R.layout.simple_list_item_1,
            items
        );

        listView.setAdapter(adapter);

        listView.setOnItemClickListener(
            (parent, view, position, id) -> {
                startActivity(new android.content.Intent(this, AyahActivity.class));
            }
        );

        root.addView(
            listView,
            new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                0,
                1
            )
        );

        setContentView(root);
    }

    public void onSurahClick(View view) {
        int number = (Integer) view.getTag();

                startActivity(new android.content.Intent(this, AyahActivity.class));
    }
}
