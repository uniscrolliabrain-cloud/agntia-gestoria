import argparse


def main():
    parser = argparse.ArgumentParser(description='Estudio de gestoría administrativa para humanos y agentes')
    parser.add_argument('--host',default='127.0.0.1')
    parser.add_argument('--port',type=int,default=8010)
    args = parser.parse_args()
    import uvicorn
    uvicorn.run('agntia_gestoria.app:create_app',factory=True,host=args.host,port=args.port,workers=1)


if __name__=='__main__':
    main()
