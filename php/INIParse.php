<?php

/**
 * A INI parser
 */
class INIParse
{
	public $commentSymbol = array(';');
	public $sectionSymbol = array('[', ']');
	public $stringSymbol = array('\'', '\'');
	public $trueBooleanSymbol = array('true',);
	public $falseBooleanSymbol = array('false',);
	public $includeSymbol = '@include ';
	public $delimiters = array('=', ':');
	public $sectionDelimiters = '.';
	public $fileList = array();
	public $readFileList = array();
	public $readFileEncoding = null;
	public $resultDict = array();
	protected $cursor = array();

    public function __construct()
    {

    }
	public function read()
	{

	}
	public function readFile()
	{

	}
    public function readString()
    {

    }
    public function readArray()
    {

    }
    protected function _read()
    {

    }
    protected function parseInclude()
    {

    }
    protected function parseSection()
    {

    }
    protected function parseExpression()
    {

    }
    protected function checkVariable()
    {

    }

    protected function getVariable()
    {

    }
    public function refresh()
    {}
    public function sections()
    {}
    public function getSection()
    {}
    public function setSection()
    {}
    public function getInt()
    {}
    public function getFloat()
    {}
    public function getBool()
    {}
    public function getString()
    {}
    public function isNull()
    {}
    public function has()
    {}
    public function writeFile()
    {}
    public function stringify()
    {}
    protected function sectionStringify()
    {}
}
