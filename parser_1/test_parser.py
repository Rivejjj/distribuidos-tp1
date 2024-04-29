import unittest
from parser_1.csv_parser import CsvParser

class TestUtils(unittest.TestCase):
    line_0 = "distributed systems,description,authors,image,preview_link,publisher,2019,info_link,category;category2,ratings_count"

    line_1 = "Its Only Art If Its Well Hung!,,['Julie Strain'],http://books.google.com/books/content?id=DykPAAAACAAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api,http://books.google.nl/books?id=DykPAAAACAAJ&dq=Its+Only+Art+If+Its+Well+Hung!&hl=&cd=1&source=gbs_api,,1996,http://books.google.nl/books?id=DykPAAAACAAJ&dq=Its+Only+Art+If+Its+Well+Hung!&hl=&source=gbs_api,['Comics & Graphic Novels'],"



    def test_parse_base_line(self): 
        parser = CsvParser()
        fields = parser.parse_csv(self.line_0)
        self.assertEqual(fields[0], 'distributed systems')
        self.assertEqual(fields[1], 'description')
        self.assertEqual(fields[2], 'authors')
        self.assertEqual(fields[3], 'image')
        self.assertEqual(fields[4], 'preview_link')
        self.assertEqual(fields[5], 'publisher')
        self.assertEqual(fields[6], '2019')
        self.assertEqual(fields[7], 'info_link')
        self.assertEqual(fields[8], 'category;category2')
        self.assertEqual(fields[9], 'ratings_count')

    def test_parse_normal_line(self):
        parser = CsvParser()
        fields = parser.parse_csv(self.line_1)
        self.assertEqual(fields[0], 'Its Only Art If Its Well Hung!')
        self.assertEqual(fields[1], '')
        self.assertEqual(fields[2], "['Julie Strain']")
        self.assertEqual(fields[3], 'http://books.google.com/books/content?id=DykPAAAACAAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api')
        self.assertEqual(fields[4], 'http://books.google.nl/books?id=DykPAAAACAAJ&dq=Its+Only+Art+If+Its+Well+Hung!&hl=&cd=1&source=gbs_api')
        self.assertEqual(fields[5], '')
        self.assertEqual(fields[6], '1996')
        self.assertEqual(fields[7], 'http://books.google.nl/books?id=DykPAAAACAAJ&dq=Its+Only+Art+If+Its+Well+Hung!&hl=&source=gbs_api')
        self.assertEqual(fields[8], "['Comics & Graphic Novels']")
        self.assertEqual(fields[9], '')
    
    def test_parse_with_commas_in_title(self):
        #LINE 19 OF BOOKS_DATA.CSV
        line =""""The Repeal of Reticence: A History of America's Cultural and Legal Struggles over Free Speech, Obscenity, Sexual Liberation, and Modern Art","At a time when America's faculties of taste and judgment—along with the sense of the sacred and shameful—have become utterly vacant, Rochelle Gurstein's The Repeal of Reticence delivers an important and troubling warning. Covering landmark developments in America's modern culture and law, she charts the demise of what was dismissively called ""gentility"" in the face of First Amendment triumphs for journalists, sex educators, and novelists—from Margaret Sanger's advocacy of birth control to Judge Woolsey's celebrated defense of Ulysses. Weaving together a study of the legal debates over obscenity and free speech with a cultural study of the critics and writers who framed the issues, Gurstein offers a trenchant reconsideration of the sacred value of privacy.",['Rochelle Gurstein'],http://books.google.com/books/content?id=6vYwCwAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api,"http://books.google.nl/books?id=6vYwCwAAQBAJ&printsec=frontcover&dq=The+Repeal+of+Reticence:+A+History+of+America%27s+Cultural+and+Legal+Struggles+over+Free+Speech,+Obscenity,+Sexual+Liberation,+and+Modern+Art&hl=&cd=1&source=gbs_api",Hill and Wang,2016-01-05,https://play.google.com/store/books/details?id=6vYwCwAAQBAJ&source=gbs_api,['Political Science'],"""

        parser = CsvParser()
        fields = parser.parse_csv(line)
        expected_title = '"The Repeal of Reticence: A History of America\'s Cultural and Legal Struggles over Free Speech, Obscenity, Sexual Liberation, and Modern Art"'
        self.assertEqual(fields[0], expected_title )

        expected_description = '"At a time when America\'s faculties of taste and judgment—along with the sense of the sacred and shameful—have become utterly vacant, Rochelle Gurstein\'s The Repeal of Reticence delivers an important and troubling warning. Covering landmark developments in America\'s modern culture and law, she charts the demise of what was dismissively called ""gentility"" in the face of First Amendment triumphs for journalists, sex educators, and novelists—from Margaret Sanger\'s advocacy of birth control to Judge Woolsey\'s celebrated defense of Ulysses. Weaving together a study of the legal debates over obscenity and free speech with a cultural study of the critics and writers who framed the issues, Gurstein offers a trenchant reconsideration of the sacred value of privacy."'
        self.assertEqual(fields[1], expected_description)

        self.assertEqual(fields[2], "['Rochelle Gurstein']")

        self.assertEqual(fields[3], 'http://books.google.com/books/content?id=6vYwCwAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api')

        expected_image = '"http://books.google.nl/books?id=6vYwCwAAQBAJ&printsec=frontcover&dq=The+Repeal+of+Reticence:+A+History+of+America%27s+Cultural+and+Legal+Struggles+over+Free+Speech,+Obscenity,+Sexual+Liberation,+and+Modern+Art&hl=&cd=1&source=gbs_api"'
        self.assertEqual(fields[4], expected_image)

        self.assertEqual(fields[5], 'Hill and Wang')

        self.assertEqual(fields[6], '2016-01-05')

        self.assertEqual(fields[7], 'https://play.google.com/store/books/details?id=6vYwCwAAQBAJ&source=gbs_api')

        self.assertEqual(fields[8], "['Political Science']")

        self.assertEqual(fields[9], '')

                    


        
