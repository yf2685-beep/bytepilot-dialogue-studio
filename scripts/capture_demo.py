"""Capture a local BytePilot writing workflow with fictional characters."""
import mongomock
from demo_capture import Recorder, browser_session, load, options


def main():
    args = options(__file__, 'bytepilot-workflow.gif')
    module = load('bytepilot_demo_app', args.root / 'web_app/app.py')
    app = module.create_app(testing=True)
    app.db = mongomock.MongoClient().forum_db
    with browser_session(app, args) as (context, page, base):
        response = context.request.post(base+'/register', form={
            'username': 'Demo Writer', 'email': 'writer@example.test',
            'password': 'fictional-local-demo', 'confirm-password': 'fictional-local-demo'})
        assert response.ok
        for name, nickname in [('Mira Chen','Mira'), ('Leo Park','Leo'), ('Nova Reed','Nova')]:
            response = context.request.post(base+'/addcharacter', form={
                'name': name, 'nickname': nickname, 'fandom': 'The Midnight Library',
                'pic': '/static/images/default.png'})
            assert response.ok
        rec = Recorder(page, 'BytePilot', 'Fictional characters / local publication only')
        page.on('dialog', lambda dialog: dialog.accept())
        page.goto(base+'/characters', wait_until='networkidle')
        rec.snap('01 / Choose a cast of characters', 1600)
        page.goto(base+'/createforum', wait_until='networkidle')
        rec.type('#forum-title', 'The library after midnight', '02 / Give the story a title')
        for name in ['Mira','Leo']:
            page.locator('#character-search-input').fill(name)
            page.wait_for_timeout(150)
            rec.snap('02 / Select characters for the conversation', 400)
            page.locator('#character-search-results > *').first.click()
            page.locator('#character-search-input').fill('')
        page.locator('#posts-container select').first.select_option(index=1)
        rec.type('#posts-container textarea', 'The lights are on. I thought this library closed years ago.',
                 '03 / Write the first character\'s post', chunks=9)
        rec.click('#add-post-btn', '03 / Add a reply from another character')
        page.locator('#posts-container select').nth(1).select_option(index=2)
        textarea = page.locator('#posts-container textarea').nth(1)
        textarea.scroll_into_view_if_needed()
        reply = 'Then who left this book here? It has tomorrow\'s date.'
        for i in range(1, 8):
            textarea.fill(reply[:round(len(reply)*i/7)])
            rec.snap('03 / Write the reply', 140)
        rec.snap('03 / Review the conversation', 1000)
        rec.click('#publish-btn', '04 / Publish inside the local demo')
        page.wait_for_url('**/viewthread/**', timeout=15000)
        page.wait_for_load_state('networkidle')
        assert 'The library after midnight' in page.locator('body').inner_text()
        assert 'tomorrow' in page.locator('body').inner_text()
        rec.snap('04 / Read the finished forum-style thread', 1600)
        rec.scroll(400, '04 / Read the finished forum-style thread')
        rec.snap('04 / Read the finished forum-style thread', 1800)
        rec.save(args.output)
    print('Verified: actual UI publish reaches the saved thread with both posts')


if __name__ == '__main__':
    main()
