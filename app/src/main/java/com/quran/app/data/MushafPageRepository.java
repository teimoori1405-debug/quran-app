package com.quran.app.data;

import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

public class MushafPageRepository {

    private final Context context;

    public MushafPageRepository(Context context) {
        this.context = context.getApplicationContext();
    }

    public List<AyahItem> getPage(int pageNumber) {

        List<AyahItem> result = new ArrayList<>();

        SQLiteDatabase db = openDatabase();

        Cursor cursor = db.rawQuery(
            "SELECT s.number, s.name_ar, a.ayah_number, a.text_ar " +
            "FROM ayah_pages ap " +
            "JOIN pages p ON p.id = ap.page_id " +
            "JOIN ayahs a ON a.id = ap.ayah_id " +
            "JOIN surahs s ON s.id = a.surah_id " +
            "WHERE p.page_number = ? " +
            "ORDER BY a.global_number",
            new String[]{String.valueOf(pageNumber)}
        );

        while (cursor.moveToNext()) {

            result.add(
                new AyahItem(
                    cursor.getInt(0),
                    cursor.getString(1),
                    cursor.getInt(2),
                    cursor.getString(3)
                )
            );
        }

        cursor.close();
        db.close();

        return result;
    }

    private SQLiteDatabase openDatabase() {

        File dbFile = context.getDatabasePath("quran.db");

        if (!dbFile.exists()) {
            dbFile.getParentFile().mkdirs();
            copyDatabase(dbFile);
        }

        return SQLiteDatabase.openDatabase(
            dbFile.getPath(),
            null,
            SQLiteDatabase.OPEN_READONLY
        );
    }

    private void copyDatabase(File destination) {

        try {

            InputStream input =
                context.getAssets().open("data/quran.db");

            FileOutputStream output =
                new FileOutputStream(destination);

            byte[] buffer = new byte[8192];
            int length;

            while ((length = input.read(buffer)) > 0) {
                output.write(buffer, 0, length);
            }

            output.flush();
            output.close();
            input.close();

        } catch (Exception e) {

            throw new RuntimeException(
                "Cannot copy quran.db",
                e
            );
        }
    }

    public static class AyahItem {

        public final int surahNumber;
        public final String surahName;
        public final int ayahNumber;
        public final String text;

        public AyahItem(
            int surahNumber,
            String surahName,
            int ayahNumber,
            String text
        ) {
            this.surahNumber = surahNumber;
            this.surahName = surahName;
            this.ayahNumber = ayahNumber;
            this.text = text;
        }
    }
}
